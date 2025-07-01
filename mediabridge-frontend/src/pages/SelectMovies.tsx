import MovieList from "../components/MovieList";
import MovieSearch from "../components/MovieSearch";
import { Movie } from "../types/Movie.ts";
import { useState } from "react";

const SelectMovies = ({
  movies,
  addMovie,
  removeMovie,
}: {
  movies: Movie[];
  addMovie: (movie: Movie) => void;
  removeMovie: (id: string) => void;
}) => {
  const [recommendations, setRecommendations] = useState<string[]>([]);
  console.log(recommendations);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top full-width section */}
      <div className="w-screen">
        <div className="max-w-screen-mx flex justify-center">
          <MovieSearch movies={movies} addMovie={addMovie} setRecommendations={setRecommendations} />
        </div>
      </div>

      {/* Content section below */}
      {
        recommendations.length > 0 ?
        <div>
          {recommendations.map(recommendation => (<div key={recommendation}>{recommendation}</div>))}
          </div>
        :
        <div className="px-4 py-8">
        <MovieList movies={movies} removeMovie={removeMovie} />
      </div>
      }

    </div>
  );
};

export default SelectMovies;
