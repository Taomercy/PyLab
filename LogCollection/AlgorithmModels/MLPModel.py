#!/usr/bin/env python
# -*- coding:utf-8 -*-
from common import *
from sklearn.neural_network import MLPClassifier


def training_by_MLP(dirname, job_name=None, scheduler=False, feature_d=0, data_processing=False):
    print "[job: %s] training by MLP" % job_name
    context = {}

    mlp = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 5), random_state=1)
    doc = DocLogs(dirname, processing=data_processing)
    vectors_docs, labels = doc.GetDocDataSet()

    finalData2d, rawMat2d = DataPCA(vectors_docs, 2)

    plot_path_list = []
    if not scheduler:
        plot_path = plotBestFit(finalData2d, rawMat2d)
        plot_path_list.append(plot_path)

        plot_path = visual_2D_dataset(array(finalData2d), array(labels),
                                      fig_title='all train data 2d', fig_name='all_train_data2d.png')
        plot_path_list.append(plot_path)

        finalData3d, rawMat3d = DataPCA(vectors_docs, 3)
        plot_path = scatter_plot3d(array(finalData3d, dtype='float'), labels,
                                   fig_title='all train data 3d', fig_name='all_train_data3d.png')
        plot_path_list.append(plot_path)

    if feature_d != 0:
        vectors_docs = array(DataPCA(vectors_docs, feature_d)[0], dtype='float')

    X_train, X_test, y_train, y_test = train_test_split(vectors_docs, labels, test_size=0.30)

    if not scheduler:
        plot_path = visual_2D_dataset(array(X_test), array(y_test),
                                      fig_title='test data', fig_name='test_data.png')
        plot_path_list.append(plot_path)

    start_time = time.clock()
    mlp.fit(X_train, y_train)
    end_time = time.clock()
    duration = end_time - start_time

    joblib.dump(mlp, get_mlp_model_path(job_name=job_name))

    mlp_predicted = mlp.predict(X_test)
    mpl_metrics_report = metrics.classification_report(y_test, mlp_predicted)
    mlp_metrics_score = metrics.accuracy_score(y_test, mlp_predicted)

    InitMLModel()
    score_param = {}
    score_param['job'] = Job.objects.get(name=job_name)
    score_param['dataset_num'] = len(labels)
    score_param['score'] = mlp_metrics_score
    score_param['duration'] = duration
    if data_processing is False:
        score_param['model'] = MLModel.objects.get(name='mlp')
    else:
        score_param['model'] = MLModel.objects.get(name='mlp+processing')

    ScoreStatistic.objects.create(**score_param)

    if not scheduler:
        plot_path = visual_2D_dataset(array(X_test), array(mlp_predicted),
                                      fig_title='mlp predict result', fig_name='mlp_predict.png')
        plot_path_list.append(plot_path)

    if not scheduler:
        context['mlp_predicted'] = mlp_predicted
        context['mlp_metrics_score'] = mlp_metrics_score
        context['mlp_metrics_report'] = mpl_metrics_report
        context['images'] = plot_path_list
        print "plot_path_list:", plot_path_list
    return context


def predict_by_MLP(dirname, job_name=None, feature_d=0):
    class PerdictInfo(object):
        def __init__(self, log, predict_label):
            self.log = log
            self.predict_label = predict_label
    print "predicting by MLP"
    context = {}
    try:
        mlp = joblib.load(get_mlp_model_path(job_name=job_name))
    except Exception as e:
        print e
        print "go to training the model"
        return
    p_doc = DocLogs(dirname)
    p_vectors_docs = p_doc.GetDocDataSet()[0]
    logs_list = p_doc.GetLogList()

    if feature_d != 0:
        p_vectors_docs = array(DataPCA(p_vectors_docs, feature_d)[0], dtype='float')

    predicted = mlp.predict(p_vectors_docs)
    print "predicted:", predicted

    context['predicted'] = [PerdictInfo(log, p_label) for log, p_label in zip(logs_list, predicted)]

    return context
