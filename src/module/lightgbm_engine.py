import os
import pdb
import gc
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Any, Dict
from dataclasses import dataclass, field
from loguru import logger
import lightgbm as lgb
import optuna
from sklearn.model_selection import train_test_split, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from ..enum_list import LIGHTGBM
from src.module.decorator_time import measure_time
from src.module.decorator_retry import retry

@dataclass
class LightGBMRegressorTuner:
    best_params: Dict[str, Any] = field(default_factory=dict)
    study: optuna.Study = None
    pipeline: Pipeline = None
    X_train: pd.DataFrame = None
    X_test: pd.DataFrame = None
    y_train: pd.Series = None
    y_test: pd.Series = None

    def preprocessing(self, df_input:pd.DataFrame, target_series:pd.Series, config:dict) -> None:
        """モデル構築の事前準備"""
        try:
            self.n_trials = LIGHTGBM.n_trials.value
            self.test_size = LIGHTGBM.test_size.value
            self.random_state = LIGHTGBM.seed.value
            self.n_jobs = config['model1']['n_process']
            self.verbose = config['model1']['verbose']
            logger.info(f"LightGBM Seed:{self.random_state}")
            
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                df_input, target_series, test_size=self.test_size, random_state=self.random_state
                )
        except Exception as e:
            logger.exception("Error at LightGBMRegressorTuner.preprocessing:")

    def objective(self, trial:optuna.Trial) -> float:
        """OptunaのObjective関数"""
        try:
            # 最適化するハイパーパラメータは優先度高いだけのものに絞る
            params = {
                "objective": "regression",
                "metric": "rmse",
                "verbosity": self.verbose,
                "boosting_type": "gbdt",
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                #"num_leaves": trial.suggest_int("num_leaves", 20, 200),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                "n_estimators": 10_000,
                "min_child_samples": 10,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
                "reg_alpha": trial.suggest_float("reg_alpha", 0.1, 10.0),
                "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 100.0),
                "random_state": self.random_state
                }

            kf = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
            rmses = []
            for train_idx, val_idx in kf.split(self.X_train):
                X_tr, X_val = self.X_train.iloc[train_idx], self.X_train.iloc[val_idx]
                y_tr, y_val = self.y_train.iloc[train_idx], self.y_train.iloc[val_idx]

                scaler = StandardScaler()
                X_tr_scaled = scaler.fit_transform(X_tr)
                X_val_scaled = scaler.transform(X_val)

                model = lgb.LGBMRegressor(**params)

                model.fit(
                    X_tr_scaled, y_tr,
                    eval_set=[(X_val_scaled, y_val)],
                    eval_metric="rmse",
                    callbacks=[lgb.early_stopping(stopping_rounds=30)],
                    )

                preds = model.predict(X_val_scaled)
                rmse = np.sqrt(np.mean(np.square(y_val - preds)))
                rmses.append(rmse)

                del model
                gc.collect()

            return np.mean(rmses)
        except RuntimeError as e:
            logger.warning("model returned None. Skipping...")
            return float(10000)
        except Exception as e:
            logger.exception("Error at LightGBMRegressorTuner.objective:")

    @measure_time
    @retry()
    def tune(self) -> None:
        """ハイパーパラメータ取得"""
        logger.info("Optimization starting...")
        self.study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=LIGHTGBM.seed.value))
        self.study.optimize(self.objective, n_trials=self.n_trials)
        self.best_params = self.study.best_trial.params
        logger.info("Optimization ended.")
        
    def train_final_model(self) -> None:
        """最適化したパラメータでモデル構築"""
        try:
            logger.info("Creating model with best params.")

            X_tr, X_val, y_tr, y_val = train_test_split(
                self.X_train, self.y_train, test_size=self.test_size, random_state=self.random_state
                )

            scaler = StandardScaler()
            X_tr_scaled = scaler.fit_transform(X_tr)
            X_val_scaled = scaler.transform(X_val)

            model = lgb.LGBMRegressor(**params)

            model.fit(
                X_tr_scaled, y_tr,
                eval_set=[(X_val_scaled, y_val)],
                eval_metric="rmse",
                callbacks=[lgb.early_stopping(stopping_rounds=30)],
                )

            self.pipeline = Pipeline([
                ("scaler", scaler),
                ("model", model)
                ])
            logger.info("Model created.")
        except Exception as e:
            logger.exception("Error at LightGBMRegressorTuner.train_final_model.")


    def evaluate(self, config):
        """テストデータでスコア確認"""
        try:
            X_test_scaled = self.pipeline.named_steps["scaler"].transform(self.X_test)
            preds = self.pipeline.named_steps["model"].predict(X_test_scaled)
            rmse = np.sqrt(np.mean(np.square(self.y_test - preds)))
            print(f"Test RMSE: {rmse:.4f}")
            logger.info(f"Test RMSE: {rmse:.4f}")

            if config['model1']['save_model']:
                model1_name = f"{config['model']}_lightgbm_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                logger.info(f"Saving {config['model']}:./model/{model1_name}")
                model1_dir = os.path.join('data', model1_name)
                self.pipeline.named_steps['model'].booster_.save_model(model1_dir)
        except Exception as e:
            logger.exception("Error at LightGBMRegressorTuner.evaluate:")

