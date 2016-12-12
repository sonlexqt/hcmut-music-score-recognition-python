import numpy as np
import cv2

symbols = cv2.imread('symbols.jpg')
symbols_gray = cv2.cvtColor(symbols, cv2.COLOR_BGR2GRAY)
# Original image: ((21 * 50), (20 * 50)) = (1050, 1000)

# Split the image to 21 * 20 = 950 cells, each 50x50 size
cells = [np.hsplit(row, 20) for row in np.vsplit(symbols_gray, 21)]

# Make it into a Numpy array. It size will be (21, 20, 50, 50)
x = np.array(cells)

# Now we prepare train_data and test_data.
# -1 means that dimension is inferred
# train = x[all the rows, 10 first columns] = (21, 10, 50, 50) => (210, 2500)
train = x[:, :10].reshape(-1, 2500).astype(np.float32)  # size = (210, 2500)
# test = x[all the rows, 10 last columns] = (21, 10, 50, 50) => (210, 2500)
test = x[:, 10:20].reshape(-1, 2500).astype(np.float32)  # size = (210,400)

# Create labels for train and test data
k = np.arange(21)
train_labels = np.repeat(k, 210 / 21)[:, np.newaxis]  # size = (210, 1)
test_labels = train_labels.copy()

# save the data
np.savez('symbols_knn_data.npz', train=train, train_labels=train_labels)
# Now load the data
with np.load('symbols_knn_data.npz') as data:
    train = data['train']
    train_labels = data['train_labels']

# Initiate the kNN, train the data, then test it with test data for k=1
knn = cv2.ml.KNearest_create()
# cv2.ml.ROW_SAMPLE means a single sample occupies one row
knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)
ret, result, neighbours, dist = knn.findNearest(test, k=5)

# Check the accuracy of classification
# For that, compare the result with test_labels and check which are wrong
matches = result == test_labels
correct = np.count_nonzero(matches)
accuracy = correct * 100.0 / result.size
print("accuracy", accuracy)

# Test the result with a new comer
file_name = 'symbol_5.jpg'
digit = cv2.imread(file_name)
digit_gray = cv2.cvtColor(digit, cv2.COLOR_BGR2GRAY)
digit_np_array = np.array(digit_gray)
new_comer = digit_np_array.reshape(-1)[:, np.newaxis].astype(np.float32).T  # size (1, 2500) {train: (210, 2500)}
ret, results, neighbours, dist = knn.findNearest(new_comer, k=5)
print(">>> file name:", file_name)
print("results:", results)
print("neighbours:", neighbours)
print("distance:", dist)
