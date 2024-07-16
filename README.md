# DCG-DemoApp
This repository contains a basic PyQT app with a server to run the fine-tuned Donainlifecycles Code Generator (DCG) model and showcasing the code generation.

## Overview
This repository contains a basic PyQT app with a server to run the fine-tuned Domainlifecycles Code Generator (DCG) model and showcasing the code generation.

## Installation and Setup

This application consists of two parts: `DCG_Client` and `DCG_Server`. Follow the steps below to get started.

### 1. Setting Up DCG_Server

1. **Clone the Repository**  
   On your Nvidia GPU PC or Server Host, clone the repository:
   ```bash
   git clone git@github.com:Tr33Bug/DCG-DemoApp.git
   cd DCG-DemoApp/DCG_Server
   ```

2. **Install the Requirements**  
   Install the necessary Python packages:
   ```bash
   pip install flask transformers
   pip3 install torch torchvision torchaudio

   ```
   >*PyTorch problems: If you have problems when installing or running pytotch use the installation instructions for your system from the homepage: [pytorch.org](https://pytorch.org/)*

3. **Start the Server**  
   Run the server application:
   ```bash
   python server.py
   ```
   You will be prompted with the host IP once the server is up and running.

### 2. Setting Up DCG_Client

1. **Clone the Repository**  
   On your client device, clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo/DCG_Client
   ```

2. **Install the Requirements**  
   Install the necessary Python packages:
   ```bash
   pip install PyQt5
   ```

3. **Start the Client**  
   Run the client application:
   ```bash
   python client.py
   ```

Now, you should have the `DCG_Server` running on your server host and the `DCG_Client` running on your client device, ready for use.


## Usage
Guide on how to use the application, including all available commands and options.

## Contributing
Guidelines for contributing to the project, including coding standards and pull request procedures.

## License
Information about the project's license, typically a link to the full license text.