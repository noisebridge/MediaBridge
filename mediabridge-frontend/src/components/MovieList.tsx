import { Movie } from "../types/Movie";
import MovieItem from "./MovieItem";

const MovieList = ({ movies }: { movies: Movie[] }) => {
  return (
    <div className="flex justify-center">
      {movies.map((movie) => (
        <MovieItem movie={movie} key={movie.id} />
      ))}
    </div>
  );
};

export default MovieList;
