from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np

class UserPredictor:
    def __init__(self):
        self.model = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(random_state = 42, max_iter = 1000) )
        ])
        self.xcols = None
        
    def add_logs_as_features(self, users_df, logs_df):
        logs_aggregated = logs_df.groupby('user_id').agg(
            total_seconds=('seconds', 'sum'),
            total_visits=('url', 'count'),
            unique_pages=('url', 'nunique'),
            laptop_visits=('url', lambda x: np.sum(x == '/laptop.html'))
        ).reset_index()

        users_df = users_df.merge(logs_aggregated, on='user_id', how='left')

        users_df['total_seconds'] = users_df['total_seconds'].fillna(0)
        users_df['total_visits'] = users_df['total_visits'].fillna(0)
        users_df['unique_pages'] = users_df['unique_pages'].fillna(0)
        users_df['laptop_visits'] = users_df['laptop_visits'].fillna(0)

        return users_df

    def fit(self, train_users, train_logs, train_y):
        
        train_users = self.add_logs_as_features(train_users, train_logs)
        
        train_data = train_users.merge(train_y, on='user_id')
        
        self.xcols = ['age', 'past_purchase_amt', 'total_seconds', 
                      'total_visits', 'unique_pages', 'laptop_visits']
        
        X = train_data[self.xcols]
        y = train_data['y']
        
        self.model.fit(X, y)
        
    def predict(self, test_users, test_logs):
        
        test_users = self.add_logs_as_features(test_users, test_logs)
        
        X_test = test_users[self.xcols]
        
        return self.model.predict(X_test)
