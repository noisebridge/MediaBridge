import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Movie } from "@/types/Movie";

const MovieItem = ({
  movie,
  onRemove,
}: {
  movie: Movie;
  onRemove: () => void;
}) => {
  return (
    <Card className="flex flex-col items-center mx-2 w-64 text-center break-words">
      <CardHeader className="w-full px-4">
        <div className="flex justify-between items-center w-full">
          <CardTitle className="text-base text-left">{movie.title}</CardTitle>
          <button
            onClick={onRemove}
            className="w-6 h-6 rounded-full bg-red-500 text-white text-xs flex items-center justify-center hover:bg-red-600 transition-colors"
            aria-label="Remove movie"
          >
            ✕
          </button>
        </div>
      </CardHeader>
      <CardContent>
        <img
          src={movie.image}
          alt={movie.title}
          className="w-full h-auto object-contain"
        />
      </CardContent>
      <CardFooter className="text-sm text-gray-500">{movie.year}</CardFooter>
    </Card>
  );
};

export default MovieItem;