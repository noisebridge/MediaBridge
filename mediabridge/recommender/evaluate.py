from lightfm.data import Dataset
from MediaBridge.mediabridge.engine.recommendation_engine import RecommendationEngine
from sklearn.model_selection import KFold

dataset = Dataset()
dataset.fit(users=[], items=[])

kf = KFold(n_splits=10, shuffle=True)


def evaluate(model: type[RecommendationEngine], dataset):
    for i, (train_index, test_index) in enumerate(kf.split(dataset)):
        training_users = [dataset[i] for i in train_index]
        testing_users = [dataset[i] for i in test_index]
        engine = model()
        engine.train(training_users)
        for test in testing_users:
            # Average precision at k for all users picked for testing
            engine.recommend(test)
        print(f"Fold {i}:")
        print(f"Precision at k:")
        print(f"std dev.:")
