import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Movie } from "@/types/Movie";
import { useState } from "react";
import { ThumbsUp, ThumbsDown, Trash2 } from "lucide-react";


const MovieItem = ({
  movie,
  onRemove,
}: {
  movie: Movie;
  onRemove: () => void;
}) => {
  const [liked, setLiked] = useState<"up" | "down" | null>(null);
  return (
    <Card
      className="flex flex-col items-center mx-2 w-64 text-center break-words"
      id={`movie-card`}
    >
      <CardHeader className="w-full px-3 pt-2 pb-2">
        <div className="flex justify-end items-center gap-2 w-full mb-2">
          <button
            type="button"
            aria-label="Toggle like/dislike"
            onClick={() => setLiked((prev) => (prev === "up" ? "down" : "up"))}
            className="p-1 transition-transform hover:scale-110 bg-transparent"
          >
            {liked === "down" ? (
              <ThumbsDown className="w-5 h-5" stroke="red" fill="#f87171" strokeWidth={2}/>
            ) : (
              <ThumbsUp className="w-5 h-5" stroke="green" fill="#4ade80" strokeWidth={2}/>
            )}
          </button>
          <button
            onClick={onRemove}
            className="p-1 hover:scale-110 transition-transform bg-transparent"
            aria-label="Remove movie"
          >
            <Trash2 className="w-5 h-5" stroke="red" fill="#f87171" strokeWidth={2} />
          </button> 
        </div>
        <CardTitle className="text-base text-center mt-2 mb-3 w-full">
          {movie.title}
        </CardTitle>
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