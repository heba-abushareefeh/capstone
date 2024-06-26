import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder,PolynomialFeatures
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import r2_score
import streamlit as st


def get_data(file_path: str):
    """
    This function load dataset from csv file

    Example
    -------
    >>> from project import get_data
    >>> df = get_data("./myDataset.csv")
    
    
    Parameters:
    -----------
    file_path: str (path of dataset)
    
    Returns:
        pandas.DataFrame

    """

    
    return pd.read_csv(file_path)
    
    


def get_info(df: pd.DataFrame, target=None):

    numeric_columns = df.select_dtypes(np.number).columns.values
    non_numeric_columns = df.columns.drop(numeric_columns).values

    numeric_info = None
    if len(numeric_columns):
        numeric_info = pd.DataFrame(
            index=numeric_columns,
            columns=[
                "mean",
                "std",
                "min",
                "max",
                "null count",
                "unique count",
            ],
        )

        numeric_info["mean"] = df[numeric_columns].mean()
        numeric_info["std"] = df[numeric_columns].std()
        numeric_info["min"] = df[numeric_columns].min()
        numeric_info["min"] = df[numeric_columns].min()
        numeric_info["max"] = df[numeric_columns].max()
        numeric_info["null count"] = df[numeric_columns].isna().sum()
        numeric_info["unique count"] = df[numeric_columns].nunique()

    non_numeric_info = None
    if len(non_numeric_columns):
        non_numeric_info = pd.DataFrame(
            index=non_numeric_columns,
            columns=[
                "unique",
                "mode",
                "freq",
                "null count",
                "unique count",
            ],
        )

        non_numeric_info["unique"] = df[non_numeric_columns].nunique()
        non_numeric_info["mode"] = df[non_numeric_columns].mode().values[0]
        non_numeric_info["freq"] = df.describe(include=object).loc["freq"]
        non_numeric_info["null count"] = df[non_numeric_columns].isna().sum()
        non_numeric_info["unique count"] = df[non_numeric_columns].nunique()

    return (numeric_info, non_numeric_info)


def clean_data(df: pd.DataFrame):
    df = df.copy()
    # drop empty columns
    df.drop(df.columns[df.isna().all()], axis=1, inplace=True)

    # drop duplicated row
    df.drop_duplicates(keep="first", inplace=True)

    # fill missing values
    mean_imputer = SimpleImputer(missing_values=np.nan, strategy="mean")
    mode_imputer = SimpleImputer(missing_values=np.nan, strategy="most_frequent")

    numeric_columns = df.select_dtypes(np.number).columns.values
    non_numeric_columns = df.columns.drop(numeric_columns).values
    for i in numeric_columns:
        df[i] = mean_imputer.fit_transform(df[i].values.reshape(-1, 1))

    # convert bool to 0,1
    df.replace({True: "1", False: "0"}, inplace=True)

    for i in non_numeric_columns:
        df[i] = mode_imputer.fit_transform(df[i].values.reshape(-1, 1)).reshape(-1)

    return df


def encoding_data(df: pd.DataFrame, target: pd.Series = None, is_ordinal: bool = None):

    if target == None:
        target = df.select_dtypes([object, bool]).columns
    if is_ordinal == None:
        is_ordinal = [True] * len(target)

    if len(target) != len(is_ordinal):
        raise Exception(f"the length must equal")
    for o, t in zip(is_ordinal, target):
        if o:
            df[t] = LabelEncoder().fit_transform(df[t])
        else:
            df = pd.get_dummies(df, columns=[t], drop_first=True)
    return df

def scaler(df: pd.DataFrame,target:pd.Series):
    MMS=MinMaxScaler() 
    for c in target:
     df[c]=MMS.fit_transform(df[c].values.reshape(-1,1))
    return df

def split(x:pd.Series,y:pd.Series,test_size:float):
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=test_size)
    dftrain=x_train
    dftrain["y_train"]=y_train
    dftest=x_test
    dftest["y_test"]=y_test
    
    return (dftrain,dftest)

def model_train(dftrain, df_test , is_contineuos:bool):
    
 try:
    x_train = dftrain.iloc[:, :-1]  # All columns except the last one
    y_train = dftrain.iloc[:, -1]   # The last column
    x_test = df_test.iloc[:, :-1]  # All columns except the last one
    y_test = df_test.iloc[:, -1]   # The last column
    
    if is_contineuos:#regression
     
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(),
            "K-Nearest Neighbors": KNeighborsRegressor(),
            "Polynomial":PolynomialFeatures()
            
        }
        param_grids = {
            "Linear Regression": {},
            "Random Forest": {
                "n_estimators": [10, 50, 100],
                "max_depth": [None, 5, 10],
            },
            "K-Nearest Neighbors": {
                "n_neighbors": [3, 5, 10],
                "weights": ["uniform", "distance"],
            },
            "Polynomial":np.arange(1,7)
        }
        best_model_name = None
        best_model = None
        best_r2_score = -float("inf")

        # Train and evaluate each model with grid search tuning
        for name, model in models.items():
            param_grid = param_grids[name]
            grid_search = GridSearchCV(model, param_grid, cv=5)
            grid_search.fit(x_train, y_train)
            best_model_for_grid = grid_search.best_estimator_
            train_pred = best_model_for_grid.predict(x_train)
            test_pred = best_model_for_grid.predict(x_test)
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(y_test, test_pred)
            st.write(
                f"{name}:Train accuracy = {train_r2}, Test accuracy = {test_r2}"
            )
            st.write(grid_search.best_params_)

            # Update best model if the current model performs better
            if test_r2 > best_r2_score:
                best_r2_score = test_r2
                best_model = grid_search
                best_model_name = name
            st.write(f"Best Model: {best_model_name}, Best Test R^2 Score: {best_r2_score}")
            st.write(best_model.best_params_)
            grid_search.fit(x_train, y_train)
            st.write(best_model.best_estimator_)
            return best_model.best_estimator_
    else:
        models = {
            "Random Forest": RandomForestClassifier(),
            "K-Nearest Neighbors": KNeighborsClassifier(),
        }
        param_grids = {
            "Random Forest": {
                "n_estimators": [10, 50, 100],
                "max_depth": [None, 5, 10],
            },
            "K-Nearest Neighbors": {
                "n_neighbors": [3, 5, 10],
                "weights": ["uniform", "distance"],
            },
        }
        best_model_name = None
        best_model = None
        best_accuracy = 0

        # Train and evaluate each model with grid search tuning
        for name, model in models.items():
            param_grid = param_grids[name]
            grid_search = GridSearchCV(model, param_grid, cv=4)
            grid_search.fit(x_train, y_train)
            best_model_for_grid = grid_search.best_estimator_
            scores = cross_val_score(best_model_for_grid, x_train, y_train, cv=5)
            avg_accuracy = scores.mean()
            st.write(f"{name}: Average Accuracy = {avg_accuracy}")
            st.write(grid_search.best_params_)

            # Update best model if the current model performs better
            if avg_accuracy > best_accuracy:
                best_accuracy = avg_accuracy
                best_model = grid_search
                best_model_name = name

        st.write(f"Best Model: {best_model_name}, Best Accuracy: {best_accuracy}")
        st.write(best_model.best_params_)
        grid_search.fit(x_train, y_train)
        st.write(best_model.best_estimator_)
        return best_model.best_estimator_
 except:
    
    st.markdown('<span style="color:red">:x: Must do all previous steps first</span>', unsafe_allow_html=True)