import { useState } from "react";
import "./App.css";

import SelectMovies from "./pages/SelectMovies";
import Recommendations from "./pages/Recommendations";

const movies = [
  {
    id: "1",
    title: "Movie 1",
    year: 2003,
    image: "https://via.placeholder.com/150",
  },
  {
    id: "2",
    title: "Movie 2",
    year: 2004,
    image: "https://via.placeholder.com/150",
  },
];

function App() {
  return (
    <>
      <SelectMovies movies={movies} />
    </>
  );
}

export default App;
