import { useState } from "react";
import SelectMovies from "./pages/SelectMovies";
import { Movie } from "./types/Movie.ts";

function App() {
  const [movies, setMovies] = useState<Movie[]>([]);

  return (
    <div className="min-h-screen w-full flex items-center justify-center">
      <div className="mx-auto w-96 bg-gray-100 p-6 rounded-lg shadow-lg">
        <SelectMovies movies={movies} setMovies={setMovies} />
      </div>
    </div>
  );
}
export default App;