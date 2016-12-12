import numpy as np
import cv2

digits = cv2.imread('digits.png')
digits_gray = cv2.cvtColor(digits, cv2.COLOR_BGR2GRAY)
# Original image: ((5*10*20), (100*20)) = (1000, 2000)

# Split the image to 5000 cells, each 20x20 size
cells = [np.hsplit(row, 100) for row in np.vsplit(digits_gray, 50)]

# Make it into a Numpy array. It size will be (50, 100, 20, 20)
x = np.array(cells)

# Now we prepare train_data and test_data.
# -1 means that dimension is inferred
# train = x[all the rows, 50 first columns] = (50, 50, 20, 20) => (2500, 400)
train = x[:, :50].reshape(-1, 400).astype(np.float32)  # size = (2500,400)
# test = x[all the rows, 50 last columns] = (50, 50, 20, 20) => (2500, 400)
test = x[:, 50:100].reshape(-1, 400).astype(np.float32)  # size = (2500,400)

# Create labels for train and test data
k = np.arange(10)
train_labels = np.repeat(k, 2500 / 10)[:, np.newaxis]  # size = (2500, 1)
test_labels = train_labels.copy()

# Initiate the kNN, train the data, then test it with test data for k=1
knn = cv2.ml.KNearest_create()
# cv2.ml.ROW_SAMPLE means a single sample occupies one row
knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)
ret, result, neighbours, dist = knn.findNearest(test, k=5)

file_name = 'digit_3.png'
digit = cv2.imread(file_name)
digit_gray = cv2.cvtColor(digit, cv2.COLOR_BGR2GRAY)
digit_np_array = np.array(digit_gray)
new_comer = digit_np_array.reshape(-1)[:, np.newaxis].astype(np.float32).T  # size (1, 400) {train: (2500, 400)}
ret, results, neighbours, dist = knn.findNearest(new_comer, k=5)
print(">>> file name:", file_name)
print("results:", results)
print("neighbours:", neighbours)
print("distance:", dist)

# Check the accuracy of classification
# For that, compare the result with test_labels and check which are wrong
# matches = result == test_labels
# correct = np.count_nonzero(matches)
# accuracy = correct * 100.0 / result.size
# print("accuracy", accuracy)
