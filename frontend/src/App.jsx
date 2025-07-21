import React, { useState, useEffect, useMemo } from 'react';

function App() {
  // State to store the fetched feedback data
  const [feedback, setFeedback] = useState([]);
  // State for filtering feedback by rating
  const [ratingFilter, setRatingFilter] = useState(''); // Default to all ratings
  // State for sorting feedback (e.g., 'ratingAsc', 'ratingDesc')
  const [sortBy, setSortBy] = useState('none'); // Default to no specific sorting
  // State to manage loading status
  const [loading, setLoading] = useState(false);
  // State to store any error messages
  const [error, setError] = useState(null);

  // useEffect hook to fetch feedback data whenever ratingFilter changes
  useEffect(() => {
    const fetchFeedback = async () => {
      setLoading(true); // Set loading to true before fetching
      setError(null);   // Clear any previous errors

      // Construct the API URL with the rating filter
      // If ratingFilter is empty, the query parameter won't be added, fetching all feedback.
      const apiUrl = `/feedback${ratingFilter ? `?rating=${ratingFilter}` : ''}`;
      console.log(`Fetching feedback from: ${apiUrl}`); // Debugging: Log the API URL

      try {
        const response = await fetch(apiUrl);

        // Check if the HTTP response was successful (status code 200-299)
        if (!response.ok) {
          const errorText = await response.text(); // Get more details from the response body
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const data = await response.json();
        console.log('Fetched data:', data); // Debugging: Log the fetched data
        setFeedback(data); // Update the feedback state with the fetched data

      } catch (err) {
        console.error('Error fetching feedback:', err); // Debugging: Log the actual error
        setError(`Failed to load feedback: ${err.message}. Please try again.`); // Set user-friendly error message
      } finally {
        setLoading(false); // Set loading to false after fetch completes (whether success or error)
      }
    };

    fetchFeedback(); // Call the async function
  }, [ratingFilter]); // Dependency array: re-run effect when ratingFilter changes

  // useMemo to memoize the sorted feedback array.
  // This re-calculates only when 'feedback' or 'sortBy' changes.
  const sortedFeedback = useMemo(() => {
    console.log(`Sorting feedback by: ${sortBy}`); // Debugging: Log sorting action
    // Create a shallow copy to avoid mutating the original 'feedback' state
    let sortableFeedback = [...feedback];

    switch (sortBy) {
      case 'ratingAsc':
        // Sort by rating in ascending order
        return sortableFeedback.sort((a, b) => a.rating - b.rating);
      case 'ratingDesc':
        // Sort by rating in descending order
        return sortableFeedback.sort((a, b) => b.rating - a.rating);
      case 'messageAsc':
        // Sort by message alphabetically (case-insensitive)
        return sortableFeedback.sort((a, b) => a.message.localeCompare(b.message));
      case 'messageDesc':
        // Sort by message reverse alphabetically (case-insensitive)
        return sortableFeedback.sort((a, b) => b.message.localeCompare(a.message));
      default:
        // No sorting, return as is
        return sortableFeedback;
    }
  }, [feedback, sortBy]); // Dependency array: re-calculate when feedback or sortBy changes

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-inter antialiased">
      <div className="max-w-3xl mx-auto bg-white p-6 rounded-xl shadow-lg">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Feedback Dashboard</h1>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-8">
          {/* Rating Filter Dropdown */}
          <div className="flex flex-col">
            <label htmlFor="rating-filter" className="text-gray-700 text-sm font-medium mb-1">Filter by Rating:</label>
            <select
              id="rating-filter"
              onChange={(e) => {
                setRatingFilter(e.target.value);
                console.log('Rating filter changed to:', e.target.value); // Debugging: Log filter change
              }}
              value={ratingFilter}
              className="p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-200 ease-in-out"
            >
              <option value="">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars</option>
              <option value="2">2 Stars</option>
              <option value="1">1 Star</option>
            </select>
          </div>

          {/* Sort By Dropdown */}
          <div className="flex flex-col">
            <label htmlFor="sort-by" className="text-gray-700 text-sm font-medium mb-1">Sort By:</label>
            <select
              id="sort-by"
              onChange={(e) => {
                setSortBy(e.target.value);
                console.log('Sort order changed to:', e.target.value); // Debugging: Log sort change
              }}
              value={sortBy}
              className="p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-200 ease-in-out"
            >
              <option value="none">Default (No Sort)</option>
              <option value="ratingDesc">Rating (High to Low)</option>
              <option value="ratingAsc">Rating (Low to High)</option>
              <option value="messageAsc">Message (A-Z)</option>
              <option value="messageDesc">Message (Z-A)</option>
            </select>
          </div>
        </div>

        {/* Conditional Rendering: Loading, Error, or Feedback List */}
        {loading && (
          <p className="text-center text-blue-600 text-lg font-medium">Loading feedback...</p>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        {!loading && !error && (
          sortedFeedback.length > 0 ? (
            <ul className="space-y-4">
              {sortedFeedback.map((f, i) => (
                <li
                  key={f.id || i} // Use a unique ID if available, otherwise fallback to index (less ideal for dynamic lists)
                  className="bg-gray-50 p-4 rounded-lg shadow-sm border border-gray-200 flex flex-col sm:flex-row justify-between items-start sm:items-center"
                >
                  <span className="text-gray-800 text-lg font-medium mb-2 sm:mb-0">{f.message}</span>
                  <span className="text-gray-600 text-md font-semibold bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                    {f.rating} star{f.rating !== 1 ? 's' : ''}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-center text-gray-600 text-lg">No feedback available for the selected criteria.</p>
          )
        )}
      </div>
    </div>
  );
}

export default App;
