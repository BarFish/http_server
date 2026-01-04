import requests
import os


def upload_image_to_server(file_path):
    """
    שולח תמונה לשרת באמצעות בקשת POST
    """
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} was not found.")
        return

    remote_filename = os.path.basename(file_path)
    url = f"http://127.0.0.1:8080/upload?file-name={remote_filename}"

    try:
        with open(file_path, 'rb') as img_file:
            response = requests.post(url, data=img_file)

        if response.status_code == 200:
            print(f"Success! Image '{remote_filename}' uploaded.")
            print(f"Server said: {response.text}")

            get_url = f"http://127.0.0.1:8080/image?image-name={remote_filename}"
            print(f"View image at: {get_url}")
        else:
            print(f"Failed to upload. Status code: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    upload_image_to_server('test-image.jpg')
