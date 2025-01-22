#This script calls an API and downloads the datapoints form the extent of more or less the netherlands

import logging
import os
import sys
import requests

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))

# The wins50
# "https://api.dataplatform.knmi.nl/open-data/v1/datasets/wins50_wfp_nl_ts_singlepoint/versions/3/files"

class OpenDataAPI:
    def __init__(self, api_token: str):
        self.base_url = "https://api.dataplatform.knmi.nl/open-data/v1"
        self.headers = {"Authorization": api_token}

    def __get_data(self, url, params=None):
        return requests.get(url, headers=self.headers, params=params).json()

    def list_files(self, dataset_name: str, dataset_version: str, params: dict):
        return self.__get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files",
            params=params,
        )

    def get_file_url(self, dataset_name: str, dataset_version: str, file_name: str):
        return self.__get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files/{file_name}/url"
        )


def download_file_from_temporary_download_url(download_url, filename):
    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception:
        logger.exception("Unable to download file using download URL")
        sys.exit(1)

    logger.info(f"Successfully downloaded dataset file to {filename}")


def main():
    api_key = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6IjdhYWI0MzM4ZjgxYzQxMTNiOGIzODVmZjljZTZlYjEzIiwiaCI6Im11cm11cjEyOCJ9"
    dataset_name = "wins50_wfp_nl_ts_singlepoint"
    dataset_version = "3"
    logger.info(f"Fetching latest files of {dataset_name} version {dataset_version}")

    api = OpenDataAPI(api_token=api_key)

    # Adjust maxKeys to retrieve up to 5 files
    params = {
        "maxKeys": 2000,  # Retrieve number of files
        "orderBy": "created",
        "sorting": "desc",
    }

    response = api.list_files(dataset_name, dataset_version, params)
    print(response)
    # Debugging: Log the full API response
    logger.info(f"Full API Response: {response}")

    if "error" in response:
        logger.error(f"Unable to retrieve list of files: {response['error']}")
        sys.exit(1)

    # Check if files are returned
    files = response.get("files", [])
    if not files:
        logger.error("No files found for the specified region and time period.")
        sys.exit(1)

    # Debugging: Log the number of files returned
    logger.info(f"Number of files returned: {len(files)}")

    # Loop through the list of files and download each one
    for file_info in files:
        file_name = file_info.get("filename")
        if not file_name:
            logger.warning("Filename missing in API response; skipping file.")
            continue

        logger.info(f"Processing file: {file_name}")

        # Extract ix and iy values from the filename
        try:
            ix = int(file_name.split("_ix")[1].split("_")[0])
            iy = int(file_name.split("_iy")[1].split("_")[0])
        except (IndexError, ValueError) as e:
            logger.warning(f"Failed to parse ix/iy values from filename {file_name}; skipping.")
            continue

        # Check if the ix and iy values fall within the specified range
        if not (50 <= ix <= 160 and 0 <= iy <= 150):
            logger.info(f"Skipping file {file_name} due to ix/iy out of range.")
            continue

        file_url_response = api.get_file_url(dataset_name, dataset_version, file_name)
        download_file_from_temporary_download_url(
            file_url_response["temporaryDownloadUrl"], file_name
        )
        print("Downloaded file")


if __name__ == "__main__":
    main()
