import { useState } from 'react'
import './App.css'

const TRIP_CATEGORIES = [
  {
    name: 'Relax',
    icon: '🏖️',
    subcategories: ['Beach', 'Spa & Wellness', 'Island Time', 'Nature Retreats'],
  },
  {
    name: 'Adventure',
    icon: '⛰️',
    subcategories: ['Hiking & Trekking', 'Outdoor Sports', 'National Parks', 'Snow & Mountains'],
  },
  {
    name: 'Culture',
    icon: '🏛️',
    subcategories: ['Museums & History', 'Local Traditions & Religious Sites', 'Theater, Opera, Performances', 'Art Galleries'],
  },
  {
    name: 'City Life',
    icon: '🏙️',
    subcategories: ['Sightseeing', 'Shopping', 'Nightlife & Rooftop Bars', 'Cafés & Local Hangouts'],
  },
  {
    name: 'Nature',
    icon: '🌳',
    subcategories: ['Forests & Hiking Trails', 'Scenic Views', 'Lakes & Rivers', 'Wildlife & Eco-tours'],
  },
  {
    name: 'Food & Drink',
    icon: '🍜',
    subcategories: ['Local Cuisine', 'Wine or Brewery Tours', 'Fine Dining', 'Street Food Adventures'],
  },
  {
    name: 'Romantic',
    icon: '🌅',
    subcategories: ['Sunset Cruises', "Couples' Spa", 'Candlelight Dinners', 'Luxury Stays'],
  },
  {
    name: 'Family-Friendly',
    icon: '🧒',
    subcategories: ["Kids' Activities", 'Theme Parks', 'Educational Fun', 'Safe Beaches & Easy Trails'],
  },
  {
    name: 'Party & Social',
    icon: '🎉',
    subcategories: ['Festivals', 'Clubs & Dancing', 'Bar Crawls', 'Beach Parties'],
  },
  {
    name: 'Work + Travel',
    icon: '💻',
    subcategories: ['Coworking-friendly Cafés', 'Balanced Routine', 'Digital Nomad Destinations'],
  },
];

const STEPS = [
  'destination',
  'dates',
  'categories',
  'allocation',
  'review',
];

function App() {
  const [form, setForm] = useState({
    destination: '',
    airport: '',
    dateFrom: '',
    dateTo: '',
    numDays: '',
    selectedCategories: [],
    allocations: {},
  });
  const [error, setError] = useState('');
  const [showItinerary, setShowItinerary] = useState(false);
  const [step, setStep] = useState(0);

  const handleInput = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleCategorySelect = (cat) => {
    setError('');
    setForm((prev) => {
      let selected = prev.selectedCategories;
      if (selected.includes(cat)) {
        selected = selected.filter((c) => c !== cat);
      } else {
        if (selected.length >= 3) {
          setError('You can select up to 3 categories.');
          return prev;
        }
        selected = [...selected, cat];
      }
      // Reset allocations for unselected
      const newAlloc = { ...prev.allocations };
      Object.keys(newAlloc).forEach((k) => {
        if (!selected.includes(k)) delete newAlloc[k];
      });
      return { ...prev, selectedCategories: selected, allocations: newAlloc };
    });
  };

  const handleSlider = (cat, value) => {
    setForm((prev) => ({
      ...prev,
      allocations: { ...prev.allocations, [cat]: Number(value) },
    }));
  };

  const totalAllocation = form.selectedCategories.reduce(
    (sum, cat) => sum + (form.allocations[cat] || 0),
    0
  );

  const validateStep = () => {
    setError('');
    if (step === 0) {
      if (!form.destination || !form.airport) {
        setError('Please fill in destination and airport.');
        return false;
      }
    } else if (step === 1) {
      if (!form.dateFrom && !form.numDays) {
        setError('Please provide either a date range or number of days.');
        return false;
      }
    } else if (step === 2) {
      if (form.selectedCategories.length === 0) {
        setError('Please select at least one trip type.');
        return false;
      }
    } else if (step === 3) {
      if (totalAllocation !== 100) {
        setError('Total allocation must be 100%.');
        return false;
      }
    }
    return true;
  };

  const handleNext = (e) => {
    if (e) e.preventDefault();
    if (validateStep()) {
      setStep((prev) => prev + 1);
      setError('');
    }
  };

  const handleBack = (e) => {
    if (e) e.preventDefault();
    setError('');
    setStep((prev) => (prev > 0 ? prev - 1 : prev));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (validateStep()) {
      setShowItinerary(true);
      setStep(4);
    }
  };

  return (
    <div className="container">
      <h1>Trip Itinerary Planner</h1>
      <form className="trip-form" onSubmit={handleSubmit}>
        {step === 0 && (
          <div className="form-group">
            <label>Destination</label>
            <input name="destination" value={form.destination} onChange={handleInput} required />
            <label>Destination Airport</label>
            <input name="airport" value={form.airport} onChange={handleInput} required />
          </div>
        )}
        {step === 1 && (
          <div className="form-group">
            <label>Date From</label>
            <input type="date" name="dateFrom" value={form.dateFrom} onChange={handleInput} />
            <label>Date To</label>
            <input type="date" name="dateTo" value={form.dateTo} onChange={handleInput} />
            <label>Or Number of Days</label>
            <input type="number" name="numDays" min="1" value={form.numDays} onChange={handleInput} />
          </div>
        )}
        {step === 2 && (
          <div className="form-group">
            <label>Type of Trip (max 3)</label>
            <div className="categories">
              {TRIP_CATEGORIES.map((cat) => (
                <button
                  type="button"
                  key={cat.name}
                  className={
                    'category-btn' +
                    (form.selectedCategories.includes(cat.name) ? ' selected' : '')
                  }
                  onClick={() => handleCategorySelect(cat.name)}
                >
                  <span className="icon">{cat.icon}</span> {cat.name}
                  <div className="subcats">
                    {cat.subcategories.map((sub) => (
                      <span key={sub} className="subcat">{sub}</span>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
        {step === 3 && form.selectedCategories.length > 0 && (
          <div className="form-group">
            <label>Allocate your time (%)</label>
            {form.selectedCategories.map((cat) => (
              <div key={cat} className="slider-row">
                <span>{cat}</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={form.allocations[cat] || 0}
                  onChange={(e) => handleSlider(cat, e.target.value)}
                />
                <span>{form.allocations[cat] || 0}%</span>
              </div>
            ))}
            <div className="total">Total: {totalAllocation}%</div>
          </div>
        )}
        {step === 4 && (
          <div className="itinerary">
            <h2>Your Itinerary for {form.destination}</h2>
            <ul>
              {form.selectedCategories.map((cat) => (
                <li key={cat}>
                  <strong>{cat}</strong>: {form.allocations[cat]}% of your trip
                </li>
              ))}
            </ul>
            <p>
              {form.dateFrom && form.dateTo
                ? `From ${form.dateFrom} to ${form.dateTo}`
                : form.numDays
                ? `For ${form.numDays} days`
                : ''}
            </p>
          </div>
        )}
        {error && <div className="error">{error}</div>}
        <div className="stepper-controls">
          {step > 0 && step < 4 && (
            <button type="button" className="back-btn" onClick={handleBack}>
              Back
            </button>
          )}
          {step < 3 && (
            <button type="button" className="next-btn" onClick={handleNext}>
              Next
            </button>
          )}
          {step === 3 && (
            <button type="submit" className="submit-btn">
              Generate Itinerary
            </button>
          )}
        </div>
      </form>
      {showItinerary && step === 4 && (
        <div className="itinerary">
          <h2>Your Itinerary for {form.destination}</h2>
          <ul>
            {form.selectedCategories.map((cat) => (
              <li key={cat}>
                <strong>{cat}</strong>: {form.allocations[cat]}% of your trip
              </li>
            ))}
          </ul>
          <p>
            {form.dateFrom && form.dateTo
              ? `From ${form.dateFrom} to ${form.dateTo}`
              : form.numDays
              ? `For ${form.numDays} days`
              : ''}
          </p>
        </div>
      )}
    </div>
  )
}

export default App
