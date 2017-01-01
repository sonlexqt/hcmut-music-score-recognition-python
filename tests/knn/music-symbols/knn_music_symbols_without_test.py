import numpy as np
import cv2

SYMBOLS_ROWS = 22
SYMBOLS_COLUMNS = 20

symbols = cv2.imread('symbols.jpg')
symbols_gray = cv2.cvtColor(symbols, cv2.COLOR_BGR2GRAY)
# Original image: ((SYMBOLS_ROWS * 50), (SYMBOLS_COLUMNS * 50)) = (?, 1000)

# Split the image to SYMBOLS_ROWS * SYMBOLS_COLUMNS cells, each 50x50 size
cells = [np.hsplit(row, SYMBOLS_COLUMNS) for row in np.vsplit(symbols_gray, SYMBOLS_ROWS)]

# Make it into a Numpy array. It size will be (SYMBOLS_ROWS, SYMBOLS_COLUMNS, 50, 50)
x = np.array(cells)

# Now we prepare train_data
# -1 means that dimension is inferred
# train = x[all the rows, all the columns] = (SYMBOLS_ROWS, SYMBOLS_COLUMNS, 50, 50) => (SYMBOLS_ROWS * SYMBOLS_COLUMNS, 2500)
train = x[:, :].reshape(-1, 2500).astype(np.float32)  # size = (SYMBOLS_ROWS * SYMBOLS_COLUMNS, 2500)

# Create labels for train and test data
k = np.arange(SYMBOLS_ROWS)
train_labels = np.repeat(k, SYMBOLS_COLUMNS)[:, np.newaxis]  # size = (SYMBOLS_ROWS * SYMBOL_COLUMNS, 1)

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
file_name = 'symbol_18.jpg'
symbol = cv2.imread(file_name)
symbol_gray = cv2.cvtColor(symbol, cv2.COLOR_BGR2GRAY)
symbol_np_array = np.array(symbol_gray)
new_comer = symbol_np_array.reshape(-1)[:, np.newaxis].astype(np.float32).T  # size (1, 2500)
ret, results, neighbours, dist = knn.findNearest(new_comer, k=5)
print(">>> file name:", file_name)
print("results:", results)
print("neighbours:", neighbours)
print("distance:", dist)
