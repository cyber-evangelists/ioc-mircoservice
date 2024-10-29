# RAG System Using LLaMA 3.2 with knowledge base of Threatmon-feeds-IOC

## Introduction

This project implements a Retrieval-Augmented Generation (RAG) based system where users ask question related to the ThreatMon-Reports-IOC and it will response to the query. This project is completed using Micro services.

## Setting Up

Follow these steps to set up and run the project:

1. Clone the repository:
   ```
   git clone https://github.com/cyber-evangelists/ioc-mircoservice.git
   ```

2. Navigate to the project root directory:
   ```
   cd ioc-mircoservice
   ```

3. Download data from [this site](https://github.com/ThreatMon/ThreatMon-Reports-IOC) and add that folder into the same root directory
   

4. Make sure that the docker is installed on your system:
   ```
   docker --version
   ```
   If docker is not installed, run the following command:
   ```
   sudo apt install docker
   ```


5. In the same directory, create a file name ```.env``` and add following API key
   ```
   GROQ_API_KEY=your_api_key
   ```
   replace your_api_key with groq API key



6. Build the docker environment::
   ```
   docker compose up --build
   ```

7. Access the graio app by pasting this URL:
   ```
   http://localhost:7860/
   ```

8. Enter Query and click on Search button, and the response will be shown below

### Demo Video Link

 [Video Link ](Here is the loom video sir: https://www.loom.com/share22f17fb9b58146ffb3cd5903b58715f9sid=abb008fd-5ab7-41f6-9da9-0ffe318acc72)



 ### Structure Diagram

 



