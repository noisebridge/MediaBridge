import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

import SelectMovies from "./pages/SelectMovies";
import Recommendations from "./pages/Recommendations";

const movies = [
  {
    id: 1,
    title: "Movie 1",
    year: 2003,
    image: "https://via.placeholder.com/150",
  },
];

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <SelectMovies movies={movies} />
    </>
  );
}

export default App;
