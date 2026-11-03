import requests

url = "https://dev-superrag-agent.eastus.cloudapp.azure.com/ai/v3/indexing/index/local/?attribute=basic"
# headers = {
#     "Content-Type": "multipart/form-data",
#     # "Authorization": "Bearer <your_token>"  # Replace <your_token> with your actual token if required
# }
# payload = {
#     "collection_name ": "easyragdev",  # Replace with actual key-value pairs
#     "file": "@data/F01-02.Decision Rules 20200324.pdf;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
# }
headers = {
    "accept": "application/json",
}
files = {
    # "file_id": (None, "3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    "collection_name": (None, "easyragdev"),
    "file": (
        "/mnt/c/Users/Cain/Documents/data/cinnamon/general/F01-02.Decision Rules 20200324.pdf",
        open("/mnt/c/Users/Cain/Documents/data/cinnamon/general/F01-02.Decision Rules 20200324.pdf", "rb"),
        # "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}
response = requests.post(url, files=files, headers=headers)

if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Failed with status code:", response.status_code)
    print("Error:", response.text)