# 🔍 Search Ranking Quality Assessment

A comprehensive tool to assess and analyze the quality of search results from your search service. This application provides detailed metrics and visualizations to help optimize ranking algorithms and ensure better search result quality.

## 🎯 Goal

To provide specific metrics against search results for specific queries, ensuring that algorithm changes lead to improvements in search quality, diversity, and user experience.

## ✨ Features

### 1. Query Analysis
- **Original Query Display**: Shows the exact query entered by the user
- **Modified Query Display**: Shows any query modifications made by the system
- **Auto-suggest Integration**: Pulls from `auto_suggest.original_query` field

### 2. Top-K Results Analysis
- Analyzes the first **18 results** (configurable) from search results
- Comprehensive table with all required fields
- Real-time data reloading capability

### 3. Key Metrics Dashboard

#### 💰 Price Mix Analysis
- **Average Price**: Mean price across top-K results
- **Median Price**: Median price for better distribution understanding
- **Free Share**: Percentage of free materials (price = 0)
- **Free Count**: Absolute count of free materials

#### 📊 Performance Proxy Metrics
- **Mean Bestseller Rating (log)**: Logarithmic average for better distribution handling
- **Gini Coefficient**: Measures inequality in bestseller ratings
- **HHI Index**: Herfindahl-Hirschman Index for concentration analysis

#### 🎯 Content & Diversity Hygiene
- **Bundles Share**: Percentage of bundle materials
- **Seller Segments Diversity**: Unique seller segments count
- **Category Breadth**: Number of unique top-level categories
- **Grade Breadth**: Number of unique grade levels

### 4. Visual Analytics
- **Price Distribution Chart**: Histogram showing price spread
- **Bestseller Rating Distribution**: Distribution of performance metrics
- **Interactive Charts**: Built with Plotly for responsive visualization

### 5. Results Table
Comprehensive table showing top-K results with fields:
- Rank, World, ID, Title
- Material Categories, Grade Levels
- Price, Bestseller Rating, Engagement Score
- Bundle Status, Creation Date, Seller Segments

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   cd search-ranking-quality
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
search-ranking-quality/
├── app.py                 # Main Flask application
├── materials.json         # Sample search results data
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
└── README.md             # This file
```

## 🔧 Configuration

### Top-K Results
The default analysis is set to **18 results**. You can modify this in `app.py`:

```python
def calculate_metrics(materials, top_k=18):  # Change this value
```

### Data Source
The application reads from `materials.json`. To use your own data:

1. Replace `materials.json` with your search results file
2. Ensure the JSON structure matches the expected format
3. Use the reload button to refresh data

## 📊 Data Format Requirements

Your JSON file should have this structure:

```json
{
  "items": {
    "materials": [
      {
        "world": "de",
        "id": 123,
        "title": "Material Title",
        "material_categories": [...],
        "material_class_grades": [...],
        "price": 9.99,
        "bestseller_rating": 25.5,
        "engagement_score": 0.001,
        "is_bundle": false,
        "created_at": "2020-01-01 00:00:00",
        "seller_segments": ["Dragon"]
      }
    ]
  },
  "auto_suggest": {
    "original_query": "search query",
    "modified_query": "modified search query"
  }
}
```

## 🎨 Customization

### Styling
- Modify CSS in `templates/index.html`
- Responsive design with mobile-first approach
- Modern gradient backgrounds and card-based layout

### Charts
- Built with Plotly.js for interactive visualizations
- Easy to add new chart types
- Responsive chart sizing

### Metrics
- Add new metrics in `calculate_metrics()` function
- Extend the UI to display additional data
- Customize calculation methods

## 🔄 Data Reload

- **Automatic**: Data loads when the page opens
- **Manual**: Click the "🔄 Reload Data" button
- **Real-time**: Updates all metrics and visualizations

## 📱 Responsive Design

- **Desktop**: Full-featured interface with side-by-side charts
- **Tablet**: Adaptive grid layouts
- **Mobile**: Stacked layout for small screens

## 🛠️ Technical Details

### Backend
- **Flask**: Lightweight web framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Mathematical computations
- **JSON**: Data parsing and handling

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Plotly.js**: Interactive charts
- **CSS Grid/Flexbox**: Modern layout system
- **Responsive Design**: Mobile-first approach

### Key Functions
- **Gini Coefficient**: Measures inequality in distributions
- **HHI Index**: Measures market concentration
- **Logarithmic Transformations**: Better handling of skewed data

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change port in app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Data not loading**:
   - Check `materials.json` exists and is valid JSON
   - Verify file permissions
   - Check browser console for errors

3. **Charts not displaying**:
   - Ensure internet connection (for CDN libraries)
   - Check browser console for JavaScript errors

### Debug Mode
The application runs in debug mode by default. For production:

```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 🔮 Future Enhancements

- **Export Functionality**: Download metrics as CSV/PDF
- **Historical Tracking**: Compare metrics over time
- **A/B Testing**: Compare different ranking algorithms
- **Real-time Updates**: WebSocket integration for live data
- **Custom Metrics**: User-defined metric calculations
- **API Integration**: Connect to live search services

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Built with ❤️ for better search experiences**
