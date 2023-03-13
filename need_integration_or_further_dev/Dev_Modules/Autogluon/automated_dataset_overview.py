
from autogluon.features.generators.auto_ml_pipeline import AutoMLPipelineFeatureGenerator
from autogluon.tabular import TabularDataset, TabularPredictor

# from autogluon.eda.auto as auto
def main():
    # Load data
    # train_data = TabularDataset('https://autogluon.s3.amazonaws.com/datasets/Inc/train.csv')
    # test_data = TabularDataset('https://autogluon.s3.amazonaws.com/datasets/Inc/test.csv')
    test_data = TabularDataset('https://autogluon.s3.amazonaws.com/datasets/Inc/test.csv')




if __name__ == '__main__':
    predictor_loaded = main()


