# Farmers Market

## Overview

Farmers Market is a data-driven platform that helps farmers, researchers, and policymakers make smarter agricultural decisions. By combining environmental, agricultural, and economic data into a single application, Farmers Market allows users to analyze farming conditions, predict future outcomes, monitor environmental risks, and support sustainable land-use planning.

The platform combines machine learning models, interactive visualizations, community discussion tools, and reporting features to transform complex agricultural data into actionable insights.

### Project Goal

Our goal is to help farmers, researchers, and policymakers make better agricultural decisions by combining environmental, agricultural, and economic data into a unified platform that promotes sustainability, productivity, and informed planning.

## Features

### Farmers
- View farm and crop information
- Predict crop success using environmental conditions
- Explore ideal growing conditions for crops
- Save analyses and reports
- Participate in community discussions

### Researchers
- Analyze soil and environmental datasets
- Upload and compare data
- Export filtered datasets
- Explore long-term environmental trends

### Policymakers
- View regional agricultural maps
- Monitor environmental risks and community reports
- Compare regions using agricultural and economic metrics
- Generate reports for planning and decision-making
- View future predictions and recommendations

### Community Features
- Create discussion posts
- Comment on posts
- Like and dislike posts
- Share agricultural concerns and insights

## Machine Learning Models

### Crop Success Prediction Model
Predicts crop success rates based on:
- Temperature
- Precipitation
- Soil quality
- Flood risk
- Soil erosion

### Regional Suitability Prediction Model
Predicts agricultural suitability based on:
- Soil quality
- Elevation
- Flood risk
- Crop productivity
- Crop prices
- Environmental conditions

## Technology Stack

### Frontend
- Streamlit

### Backend
- Flask REST API

### Database
- MySQL

### Data & Machine Learning
- Python
- Pandas
- Scikit-Learn

## Repository Structure

```text
app/                Streamlit frontend
api/                Flask REST API
database-files/     SQL database initialization scripts
datasets/           Datasets used for analysis and ML
ml-src/             Model development and training
docs/               Project documentation
```

## Running the Application

### Clone Repository

```bash
git clone <repository-url>
cd farmers-market
```

### Start Containers

```bash
docker compose up --build
```

### Access the Application

Frontend:

```text
http://localhost:8501
```

Backend API:

```text
http://localhost:4000
```

## REST API

The application includes REST API endpoints for:

- Farms
- Crops
- Users
- Posts
- Comments
- Reactions
- Saved Analyses
- Saved Graphs
- Saved Reports
- Machine Learning Predictions

Example routes:

```http
GET /farms
POST /posts
GET /comments/post/<post_id>
POST /reactions/post/<post_id>
POST /ml/crop-success
POST /ml/policy-suitability
```

## Team

Developed as part of the Summer 2026 Belgium Dialogue of Civilizations program.

### Team Members
- Lauryn Gong
- Elise Wizemann
- Nicole Stekol
- Minju Sung

## Major Team Member Contributions

### Lauryn Gong

### Elise Wizemann

Most of my work was centered around the database and the researcher persona. I worked on mapping out the database through diagrams and then transferring them into SQL tables, and continiously updated them as the scope, details, and feasability of our website changed and through discussions with my group members. I also worked to produce most of the mock data related to the farmer persona (users, farms, user_growing_records).

For the researcher persona I spent a lot of time developing their user stories and uses for this application, especially as our ML models began to shift from their original ideas. The feedback from my professors and team members helped me a lot through this process, and through this I was able to base this persona around lots of data visualization. I also worked on a good portion of the pages for this persona, including the map, data export, and some other pages that were deleted or replaced later on into our development process.

### Nicole Stekol

### Minju Sung

## Want to learn more about our development process? Check out our [Blog!](https://lauryngong.github.io/Belgium-Politics/).