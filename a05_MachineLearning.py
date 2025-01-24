from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import statsmodels.api as sm

# Load the dataset
#path = "Harmonie_energy_WTselectedOnHeights.csv"
path = "Harmonie_energyWTsel_with_distances.csv"
data = pd.read_csv(path, delimiter=',')
print(data.columns)

# Clean column names
data.columns = data.columns.str.strip()

# Convert 'time' to datetime if it is not already
data['time'] = pd.to_datetime(data['time'], errors='coerce')
data['year'] = data['time'].dt.year
data['month'] = data['time'].dt.month
data['day'] = data['time'].dt.day
data = data.drop(columns=['time'])
print(data.columns)

# Split data into features (X) and target (y)
X = data[['WT_Longtitude', 'WT_Latitude', 'day']]
y = data['prod']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---- Random Forest Model ----
rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10, min_samples_split=5)

# Train the Random Forest model
rf.fit(X_train, y_train)

# Predict on test set using Random Forest
rf_y_pred = rf.predict(X_test)

# Evaluate Random Forest model with RMSE
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_y_pred))
print(f"Random Forest RMSE: {rf_rmse}")

# ---- Linear Regression Model ----
lr = LinearRegression()

# Train the Linear Regression model
lr.fit(X_train, y_train)

# Predict on test set using Linear Regression
lr_y_pred = lr.predict(X_test)

# Evaluate Linear Regression model with RMSE
lr_rmse = np.sqrt(mean_squared_error(y_test, lr_y_pred))
print(f"Linear Regression RMSE: {lr_rmse}")

# Coefficients of Linear Regression
coefficients = pd.DataFrame(lr.coef_, X.columns, columns=['Coefficient'])
print("Linear Regression Coefficients:")
print(coefficients)

# ---- p-values for Linear Regression ----
# Add constant (intercept) to the model for statsmodels
X_train_sm = sm.add_constant(X_train)

# Fit the model using statsmodels to obtain p-values
sm_model = sm.OLS(y_train, X_train_sm).fit()

# Print the summary including p-values
print("\nLinear Regression Summary with p-values:")
print(sm_model.summary())
