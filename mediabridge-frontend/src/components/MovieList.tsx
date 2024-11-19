import { Movie } from "../types/Movie";

const MovieList = ({ movies }: { movies: Movie[] }) => {
  return (
    <div>
      {movies.map((movie) => (
        <>
          <div key={movie.id}>
            <h2>{movie.title}</h2>
            <img src={movie.image} alt={movie.title} />
          </div>
        </>
      ))}
    </div>
  );
};

export default MovieList;
