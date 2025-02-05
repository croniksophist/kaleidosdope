import redis
import boto3
import os
import time
from PIL import Image
import cv2  # If you're processing images with OpenCV

# AWS S3 Setup
s3_client = boto3.client('s3', region_name='us-west-1')  # Change your region here
bucket_name = 'your-bucket-name'

# Redis Setup
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# AI Media Processing Function (This can be customized based on your needs)
def process_media(file_path):
    # Example: Image processing with OpenCV
    image = cv2.imread(file_path)
    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Dummy AI processing
    
    processed_file_path = "processed_" + os.path.basename(file_path)
    cv2.imwrite(processed_file_path, processed_image)
    
    return processed_file_path

# Upload to S3 Function
def upload_to_s3(file_path):
    file_name = os.path.basename(file_path)
    s3_client.upload_file(file_path, bucket_name, file_name)
    print(f"Uploaded {file_name} to S3.")
    
    # Remove the file after upload
    os.remove(file_path)

# Process files in the Redis queue
def process_files():
    while True:
        # Check if there's a file to process
        file_to_process = redis_client.lpop('media_queue')
        if file_to_process:
            file_path = file_to_process.decode('utf-8')
            print(f"Processing {file_path}...")

            # Step 1: Process the media
            processed_file = process_media(file_path)

            # Step 2: Upload processed file to S3
            upload_to_s3(processed_file)

        # Wait a bit before checking the Redis queue again
        time.sleep(2)

# Example of adding a file to the Redis queue
def add_to_queue(file_path):
    redis_client.rpush('media_queue', file_path)

# Main function
if __name__ == "__main__":
    # You can add a file to the queue like this:
    # add_to_queue("path/to/your/media/file.jpg")

    print("Starting the processing loop...")
    process_files()