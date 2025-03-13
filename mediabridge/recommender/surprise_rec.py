from surprise import SVD, Dataset
from surprise.model_selection import cross_validate


def main() -> None:
    # Load the movielens-100k dataset (download it if needed).
    data = Dataset.load_builtin("ml-100k")

    # Use the famous SVD algorithm.
    algo = SVD()

    # Run 5-fold cross-validation and print results.
    cross_validate(algo, data, measures=["RMSE", "MAE"], cv=5, verbose=True)


if __name__ == "__main__":
    main()
