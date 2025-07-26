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

const pastelBackgrounds = [
  "bg-pink-100",
  "bg-blue-100",
  "bg-green-100",
  "bg-yellow-100",
  "bg-purple-100",
  "bg-indigo-100",
  "bg-rose-100",
  "bg-orange-100",
];


const MovieItem = ({
  movie,
  onRemove,
}: {
  movie: Movie;
  onRemove: () => void;
}) => {
  const [liked, setLiked] = useState<"up" | "down" | null>(null);
  const pastelIndex = movie.year % pastelBackgrounds.length;
  const pastelBg = pastelBackgrounds[pastelIndex];
  return (
    <Card
      className={`flex flex-col items-center mx-2 w-64 text-center break-words ${pastelBg}`}
      id={`movie-card`}
    >
      <CardHeader className="w-full px-3 pt-2 pb-2">
        <div className="flex justify-end items-center gap-2 w-full mb-2">
          <button
            type="button"
            aria-label="Toggle like/dislike"
            onClick={() => setLiked((prev) => (prev === "up" ? "down" : "up"))}
              className="p-0 w-7 h-7 flex items-center justify-center bg-transparent focus:outline-none focus:ring-0"
          >
            {liked === "down" ? (
              <ThumbsDown className="p-0 w-6 h-6" stroke="red" fill="#f87171" strokeWidth={2} />
            ) : (
              <ThumbsUp className="p-0 w-6 h-6" stroke="green" fill="#4ade80" strokeWidth={2} />
            )}
          </button>
          <button
            onClick={onRemove}
            className="p-0 w-7 h-7 flex items-center justify-center bg-transparent focus:outline-none focus:ring-0"
            aria-label="Remove movie"
          >
            <Trash2 className="w-7 h-7" stroke="red" fill="#f87171" strokeWidth={2} />
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