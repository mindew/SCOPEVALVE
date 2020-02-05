import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

data = pd.read_csv("multi_classifier.csv")
categories = ['Pasta','Pies','Salads']
training_set, test_set = train_test_split(data, test_size = 0.2, random_state = 1)
X_train = training_set.iloc[:,0:4].values
X_test = test_set.iloc[:,0:4].values
classifier = SVC(kernel='linear', random_state = 1, probability=True)

for category in categories:
	classifier.fit(X_train,training_set[category])
	Y_pred = classifier.predict(X_test)
	pred = classifier.predict_log_proba(X_test)
	print(Y_pred)
	print(pred)
	print('Test accuracy is {}'.format(accuracy_score(test_set[category],Y_pred)))

#test_set["Predictions"] = Y_pred
#cm = confusion_matrix(Y_test,Y_pred)
#print(cm)
#accuracy = float(cm.diagonal().sum())/len(Y_test)
#print("\nAccuracy Of SVM For The Given Dataset : ", accuracy)