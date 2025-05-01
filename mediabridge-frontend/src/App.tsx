import SelectMovies from "./pages/SelectMovies";
import { useMovieList } from "@/hooks/useMovieList";

function App() {
  const { movies, addMovie, removeMovie } = useMovieList();

  return (
    <div className="min-h-screen bg-white px-4 pt-8">
      <SelectMovies
        movies={movies}
        addMovie={addMovie}
        removeMovie={removeMovie}
      />
    </div>
  );
}

export default App;