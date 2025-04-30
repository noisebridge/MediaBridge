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
import { toast } from "@/hooks/use-toast";
import { searchMovies } from "@/api/movie"; 


type Props = {
  movies: Movie[];
  addMovie: (movie: Movie) => void;
};

const isMoviePresent = (movies: Movie[], title: string) => {
  return movies.some((movie) => movie.title.toLowerCase() === title.toLowerCase());
};

const showErrorToast = (title: string, description?: string) => {
  toast({
    title,
    description,
    variant: "destructive",
  });
};

const MovieSearch = ({ movies, addMovie }: Props) => {
  const [title, setTitle] = useState("");

  const handleAddMovie = async () => {
    if (!title.trim()) return;
  
    try {
      const data = await searchMovies(title); 
  
      const foundMovie = data.find(
        (movie: { title: string }) => movie.title.toLowerCase() === title.toLowerCase()
      );
  
      if (!foundMovie) {
        showErrorToast("Movie not found", "Please check your spelling.");
        return;
      }

      if (isMoviePresent(movies, foundMovie.title)) {
        showErrorToast("Movie already added");
        return;
      }
  
      addMovie({
        id: foundMovie.id.toString(),
        title: foundMovie.title,
        year: foundMovie.year,
        image: `https://picsum.photos/seed/${foundMovie.id}/200/300`,
      });
  
      setTitle(""); 
    } catch (error) {
      console.error("Error searching for movie:", error);
      showErrorToast("Failed to search for movie", "Database might be down.");
    }
  };
  return (
    <Card className="w-full max-w-md flex flex-col items-center mb-4">
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
      </CardContent>
      <CardFooter>
        <Button type="submit">Get Recommendations</Button>
      </CardFooter>
    </Card>
  );
};

export default MovieSearch;