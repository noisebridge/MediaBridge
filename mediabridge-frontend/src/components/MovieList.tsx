import { Movie } from "../types/Movie";
import MovieItem from "./MovieItem";

const MovieList = ({
  movies,
  removeMovie,
}: {
  movies: Movie[];
  removeMovie: (id: string) => void;
}) => {
  return (
    <div className="flex flex-wrap justify-center gap-4 w-full">
      {movies.map((movie) => (
        <MovieItem movie={movie} key={movie.id} onRemove={() => removeMovie(movie.id)} />
      ))}
    </div>
  );
};

export default MovieList;
