import numpy as np
from collections import deque

def connected_components(mask, area_threshold=500, connectivity=8):
    """
    Perform connected component analysis on a binary mask.
    Args:
        mask (np.ndarray): 2D binary mask (0/1 or 0/255).
        area_threshold (int): Minimum area to keep a blob.
        connectivity (int): 4 or 8 for neighborhood.
    Returns:
        cleaned_mask (np.ndarray): Mask with only significant blobs.
        blobs (list): List of dicts with properties for each blob.
    """
    h, w = mask.shape
    label_mask = np.zeros_like(mask, dtype=np.int32)
    label_id = 1
    blobs = []

    # Define neighbor offsets
    if connectivity == 4:
        neighbors = [(-1,0), (1,0), (0,-1), (0,1)]
    else:
        neighbors = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]

    for y in range(h):
        for x in range(w):
            if mask[y, x] and label_mask[y, x] == 0:
                # Start BFS for new blob
                queue = deque()
                queue.append((y, x))
                label_mask[y, x] = label_id
                pixels = []

                while queue:
                    cy, cx = queue.popleft()
                    pixels.append((cy, cx))
                    for dy, dx in neighbors:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if mask[ny, nx] and label_mask[ny, nx] == 0:
                                label_mask[ny, nx] = label_id
                                queue.append((ny, nx))

                # Compute properties
                area = len(pixels)
                if area >= area_threshold:
                    ys, xs = zip(*pixels)
                    centroid = (float(np.mean(xs)), float(np.mean(ys)))
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)
                    bbox = (min_x, min_y, max_x, max_y)
                    blobs.append({
                        'label': label_id,
                        'area': area,
                        'centroid': centroid,
                        'bbox': bbox
                    })
                label_id += 1

    # Create cleaned mask
    cleaned_mask = np.zeros_like(mask)
    for blob in blobs:
        cleaned_mask[label_mask == blob['label']] = 1

    return cleaned_mask, blobs

# Example usage:
if __name__ == "__main__":
    # Example: mask = np.array([[...]], dtype=np.uint8)
    # mask should be binary (0/1)
    mask = np.random.randint(0, 2, (100, 100), dtype=np.uint8)
    cleaned_mask, blobs = connected_components(mask, area_threshold=500)
    print("Number of significant blobs:", len(blobs))
    for blob in blobs:
        print(blob)