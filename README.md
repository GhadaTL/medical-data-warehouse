# Medical Data Warehouse

An end-to-end Data Engineering project that transforms medical bibliographic XML data into a structured Data Warehouse using Python, PostgreSQL, SQL, and Power BI.

## Project Overview

This project aims to design and implement a Medical Data Warehouse from a collection of more than 4,000 PubMed-like XML files.

The main objective is to transform raw bibliographic data into structured, cleaned, and organized information that can be queried and analyzed to extract meaningful insights about scientific publications.

The project covers XML processing, data quality management, data extraction, transformation, dimensional modeling, ETL development, SQL analytics, and Power BI integration.

## Project Architecture

The project follows a traditional Data Warehouse architecture:

**XML Sources → XML Processing → Data Extraction → Data Cleaning → ETL Pipeline → PostgreSQL Data Warehouse → Power BI**

### Project Workflow

1. **XML Exploration and Validation**
   - Analyze the structure of XML files.
   - Identify valid and malformed XML documents.
   - Detect structural anomalies and missing information.

2. **XML Cleaning and Repair**
   - Repair recoverable XML files.
   - Separate valid, rejected, and repaired documents.
   - Preserve original files and generate repair reports.

3. **Data Extraction**
   - Extract bibliographic information from XML documents.
   - Retrieve publication metadata, authors, journals, keywords, languages, and MeSH terms.

4. **Data Cleaning and Quality Management**
   - Handle missing values.
   - Detect and resolve duplicate PMIDs.
   - Validate extracted information.
   - Check multivalued fields and structural consistency.

5. **Dimensional Modeling**
   - Design a dimensional model with a central fact table.
   - Create dimension tables for descriptive information.
   - Implement bridge tables to handle many-to-many relationships.

6. **ETL Development**
   - Develop Python scripts to extract, transform, and load data.
   - Load staging, dimension, bridge, and fact tables.
   - Validate data consistency and referential integrity.

7. **SQL Analytics**
   - Analyze publication trends.
   - Identify the most represented journals and authors.
   - Explore language distribution, keywords, and publication types.

8. **Power BI Integration**
   - Connect Power BI to the PostgreSQL database.
   - Import all 15 Data Warehouse tables.
   - Configure relationships between fact, dimension, and bridge tables.
   - Prepare the data model for analytical reporting and visualization.

## Data Warehouse Model

The PostgreSQL database contains 15 tables.

### Dimension Tables

- `Dim_Article`
- `Dim_Date`
- `Dim_Journal`
- `Dim_Author`
- `Dim_Language`
- `Dim_Keyword`
- `Dim_MeSH`
- `Dim_Publication_Type`

### Fact Table

- `Fact_Article`

### Bridge Tables

- `Bridge_Article_Author`
- `Bridge_Article_Language`
- `Bridge_Article_Keyword`
- `Bridge_Article_MeSH`
- `Bridge_Article_Type`

### Staging Table

- `Staging_Article`

The bridge tables handle many-to-many relationships between articles and their associated authors, languages, keywords, MeSH terms, and publication types.

The fact table stores publication-level measures and foreign keys to relevant dimensions.

## Data Processing Results

The XML processing and cleaning pipeline produced the following results:

| Metric | Result |
|---|---:|
| Original XML files | 4,036 |
| Valid processed XML files | 3,905 |
| Rejected XML files | 131 |
| Repaired XML files | 22 |
| Final cleaned bibliographic records | 3,904 |
| Unique PMIDs | 3,904 |

The final cleaned dataset contains bibliographic information such as:

- PMID and title
- Authors and affiliations
- Journal and ISSN
- Publication date
- Abstract
- Keywords
- Languages
- DOI
- Publication types
- MeSH terms

## ETL Implementation

The ETL pipeline was developed in Python, with PostgreSQL as the target database.

The loading process includes:

- Staging table loading
- Dimension loading
- Bridge table loading
- Fact table loading
- Data integrity validation

The loading scripts are available in the `scripts/` directory.

### Data Warehouse Loading Results

| Table | Number of Records |
|---|---:|
| Dim_Article | 3,904 |
| Dim_Date | 351 |
| Dim_Journal | 1,069 |
| Dim_Author | 23,062 |
| Dim_Language | 15 |
| Dim_Keyword | 7,223 |
| Dim_MeSH | 3,928 |
| Dim_Publication_Type | 38 |
| Fact_Article | 3,904 |
| Bridge_Article_Author | 28,902 |
| Bridge_Article_Language | 3,933 |
| Bridge_Article_Keyword | 12,475 |
| Bridge_Article_MeSH | 35,839 |
| Bridge_Article_Type | 7,778 |
| Staging_Article | 3,904 |

## Data Quality and Validation

Several validation checks were performed to ensure the reliability of the Data Warehouse:

- Verified PMID uniqueness in `Dim_Article`.
- Checked mandatory fields for missing values.
- Validated foreign key relationships.
- Checked for orphan records in fact and bridge tables.
- Verified publication count constraints.
- Validated multivalued fields before loading.

The validation results confirmed referential integrity across the fact and bridge tables.

## SQL Analytics

Analytical SQL queries were performed to explore the bibliographic dataset.

The analyses include:

- Number of publications by year.
- Top 10 journals by publication count.
- Top 10 authors by publication count.
- Publication language distribution.
- Most frequent keywords.
- Publication type distribution.

These queries provide insights into the scientific publications represented in the dataset.

## Power BI Integration

Power BI was successfully connected to the PostgreSQL Data Warehouse.

The following tasks were completed:

- Established a connection between Power BI and PostgreSQL.
- Imported all 15 Data Warehouse tables.
- Configured relationships between fact, dimension, and bridge tables.
- Prepared the data model for analytical reporting and visualization.

The imported model supports further exploration of publication trends, journal rankings, author contributions, languages, keywords, and publication types.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | XML processing, data cleaning, and ETL development |
| PostgreSQL | Data Warehouse storage |
| SQL | Data modeling, validation, and analytics |
| Power BI | Data integration and visualization |
| Git & GitHub | Version control and project management |

## Project Structure

```text
medical-data-warehouse/
│
├── data/
│   └── cleaned/
│       ├── articles_cleaned_provisional.csv
│       ├── bibliographic_cleaned.csv
│       └── bibliographic_extraction_raw.csv
│
├── notebooks/
│   └── exploration.ipynb
│
├── reports/
│   ├── XML classification reports
│   ├── duplicate detection reports
│   └── data quality reports
│
├── scripts/
│   ├── clean_xml.py
│   ├── explorer_xml.py
│   ├── load_staging.py
│   ├── load_dim_*.py
│   ├── load_bridge_*.py
│   ├── load_fact_article.py
│   └── validation scripts
│
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/GhadaTL/medical-data-warehouse.git
cd medical-data-warehouse
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the PostgreSQL database

Create a database named:

```text
medical_data_warehouse
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_NAME=medical_data_warehouse
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

**Important:** The `.env` file is excluded from version control to protect database credentials.

### 5. Run the ETL scripts

Execute the Python loading scripts from the project root, following the dependency order:

1. Staging
2. Dimensions
3. Bridge tables
4. Fact table

Example:

```bash
python scripts/load_staging.py
```

Then execute the remaining loading scripts according to their dependencies.

## Future Improvements

- Develop and enhance the interactive Power BI dashboard.
- Improve keyword and publication type normalization.
- Add more advanced analytical indicators.
- Automate the complete ETL workflow.
- Implement additional data quality monitoring.

## Author

Engineering student in Data Engineering and Decision Support Systems (IDSD).

Interested in Data Engineering, Data Science, and Artificial Intelligence.