<!-- ABOUT THE PROJECT -->
## About The Project

This project is an entity normalisation engine developed for the [Vector AI](https://www.vector.ai) recruitment process. It supports entity normalisation for the following types of entities:
   * Companies, businesses;
   * Products, objects;
   * Locations, cities, countries;
   * Serial numbers;
   * Street addresses.

The model takes as input a stream of strings in the classes above. There is no context provided for each entity.  

The model performs a normalisation to suitable Wikipedia articles for the first three types of entities. 
Given the uniqueness of the latter two types of entities, normalisation is performed according to linguistic similarity 
of the input entities using the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance). 

The model accepts entities in any language supported by the Google Translator API.

<!-- GETTING STARTED -->
## Getting Started

To set up this project:

1. Clone GitHub repo:
  ```sh
  git clone https://github.com/jleguina0/entity-normalization.git
  ```

2. Create a suitable virtual environment and install dependencies:
    * With `conda`:
       ```shell
       cd entity-normalization
       conda env create -f environment.yml
       conda activate entity-norm37
       ```
    * Or else, create a virtual environment with Python 3.7 and do:
        ```shell
        pip install -r requirements.txt
        ```
     

3. To run the normalization engine with some predefined examples in various languages:
   ```shell
   python entity_norm.py
   ```

<!-- CONTACT -->
## Contact

Javier Leguina Peral - jleguina0@gmail.com

Project Link: [https://github.com/jleguina0/entity-normalization](https://github.com/jleguina0/entity-normalization)
