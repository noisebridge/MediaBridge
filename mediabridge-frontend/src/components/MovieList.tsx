import { Movie } from "../types/Movie";
import MovieItem from "./MovieItem";

type Props = {
  movies: Movie[];
  removeMovie?: (id: string) => void;
};

const MovieList = ({ movies, removeMovie }: Props) => {
  return (
    <div className="flex flex-wrap justify-center gap-4 w-full">
      {movies.map((movie) => (
        <MovieItem
          movie={movie}
          key={movie.id}
          {...(removeMovie ? { onRemove: () => removeMovie(movie.id) } : {})}
        />
      ))}
    </div>
  );
};

export default MovieList;
