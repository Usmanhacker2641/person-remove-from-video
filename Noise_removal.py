import numpy as np

def pad_image(img, pad_width, pad_value=0):
    return np.pad(img, pad_width, mode='constant', constant_values=pad_value)

def erosion(binary_mask, kernel_size):
    pad = kernel_size // 2
    padded = pad_image(binary_mask, pad)
    eroded = np.zeros_like(binary_mask)
    for i in range(eroded.shape[0]):
        for j in range(eroded.shape[1]):
            region = padded[i:i+kernel_size, j:j+kernel_size]
            eroded[i, j] = np.min(region)
    return eroded

def dilation(binary_mask, kernel_size):
    pad = kernel_size // 2
    padded = pad_image(binary_mask, pad)
    dilated = np.zeros_like(binary_mask)
    for i in range(dilated.shape[0]):
        for j in range(dilated.shape[1]):
            region = padded[i:i+kernel_size, j:j+kernel_size]
            dilated[i, j] = np.max(region)
    return dilated

def noise_removal(binary_mask, kernel_size):
    # binary_mask: numpy array with values 0 (background) and 1 (foreground)
    eroded = erosion(binary_mask, kernel_size)
    cleaned = dilation(eroded, kernel_size)
    return cleaned

# Example usage:
if __name__ == "__main__":
    # Example: create a noisy binary mask
    mask = np.random.choice([0, 1], size=(20, 20), p=[0.9, 0.1])
    mask[5:15, 5:15] = 1  # Simulate a foreground object

    for k in [5, 7, 11]:
        cleaned_mask = noise_removal(mask, k)
        print(f"Cleaned mask with kernel size {k}:\n", cleaned_mask)