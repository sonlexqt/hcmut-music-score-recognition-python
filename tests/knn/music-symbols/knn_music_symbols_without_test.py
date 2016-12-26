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
# train = x[all the rows, columns] = (21, 20, 50, 50) => (420, 2500)
train = x[:, :].reshape(-1, 2500).astype(np.float32)  # size = (420, 2500)

# Create labels for train and test data
k = np.arange(21)
train_labels = np.repeat(k, 420 / 21)[:, np.newaxis]  # size = (420, 1)

# Save the data
np.savez('symbols_knn_data_full.npz', train=train, train_labels=train_labels)

# MORE
# Now load the data
with np.load('symbols_knn_data_full.npz') as data:
    train = data['train']
    train_labels = data['train_labels']

# Initiate the kNN, train the data, then test it with test data for k=1
knn = cv2.ml.KNearest_create()
# cv2.ml.ROW_SAMPLE means a single sample occupies one row
knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)

# Test the result with a new comer
file_name = 'symbol_9.jpg'
symbol = cv2.imread(file_name)
symbol_gray = cv2.cvtColor(symbol, cv2.COLOR_BGR2GRAY)
symbol_np_array = np.array(symbol_gray)
new_comer = symbol_np_array.reshape(-1)[:, np.newaxis].astype(np.float32).T  # size (1, 2500) {train: (420, 2500)}
ret, results, neighbours, dist = knn.findNearest(new_comer, k=5)
print(">>> file name:", file_name)
print("results:", results)
print("neighbours:", neighbours)
print("distance:", dist)
