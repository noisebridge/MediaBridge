import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Movie } from "../types/Movie"; 
import { searchMovies } from "@/api/movie"; 


type Props = {
  movies: Movie[];
  addMovie: (movie: Movie) => void;
};

const isMoviePresent = (movies: Movie[], title: string) => {
  return movies.some((movie) => movie.title.toLowerCase() === title.toLowerCase());
};

const MovieSearch = ({ movies, addMovie }: Props) => {
  const [title, setTitle] = useState("");
  const [warning, setWarning] = useState("");

  const handleAddMovie = async () => {
    if (!title.trim()) return;
  
    try {
      const data = await searchMovies(title); 
  
      const foundMovie = data.find(
        (movie: { title: string }) => movie.title.toLowerCase() === title.toLowerCase()
      );
  
      if (!foundMovie) {
        setWarning(`‘${title}’ not found. Please check your spelling.`);
        return;
      }

      if (isMoviePresent(movies, foundMovie.title)) {
        setWarning(`‘${title}’ already added.`);
        return;
      }
  
      addMovie({
        id: foundMovie.id.toString(),
        title: foundMovie.title,
        year: foundMovie.year,
        image: `https://picsum.photos/seed/${foundMovie.id}/200/300`,
      });
      setWarning("");
      setTitle(""); 
    } catch (error) {
      setWarning(`failed to search for movie: database might be down`);
      console.error("Error searching for movie:", error);
    }
  };
  return (
    <Card className="w-full max-w-md flex flex-col items-center">
      <CardHeader className="flex flex-col items-center text-center">
        <CardTitle>Mediabridge</CardTitle>
        <CardDescription>Add liked movies</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex w-full items-center space-x-4">
          <Input
            type="text"
            placeholder="The Room"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleAddMovie();
              }
            }}
          />
          <Button onClick={handleAddMovie}>Add Movie</Button>
        </div>
        <div
        className={`mt-4 bg-red-500 text-white px-4 py-2 rounded-md text-sm text-center transition-opacity ${
          warning ? "opacity-100" : "opacity-0 h-0 overflow-hidden"
        }`}
        role="alert"
        aria-live="polite"
      >
        {warning}
      </div>
      </CardContent>
      <CardFooter>
        <Button type="submit">Get Recommendations</Button>
      </CardFooter>
    </Card>
  );
};

export default MovieSearch;