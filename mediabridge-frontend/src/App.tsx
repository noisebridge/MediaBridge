import { useState } from "react";
import SelectMovies from "./pages/SelectMovies";
import { Movie } from "./types/Movie.ts";
import { Toaster } from "@/components/ui/toaster"; 

function App() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const removeMovie = (id: string) => {
    setMovies((prev) => prev.filter((movie) => movie.id !== id));
  };

  return (
    <div className="min-h-screen bg-white px-4 pt-8">
      <SelectMovies movies={movies} setMovies={setMovies} removeMovie={removeMovie} />
      <Toaster />
    </div>
  );
}
export default App;