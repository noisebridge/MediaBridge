import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import SearchBar  from "@/components/ui/searchbar";
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
  const [suggestions, setSuggestions] = useState<Movie[]>([]);


  const handleAddMovie = async (selectedMovie?: Movie) => {
    const movieToAdd = selectedMovie ?? null;
  
    if (!title.trim() && !movieToAdd) return;
  
    try {
      const data = await searchMovies(title);
      
      const foundMovie =
        movieToAdd ||
        data.find((movie: Movie) => movie.title === title);
  
      if (!foundMovie) {
        setWarning(`‘${title}’ not found. Please check your spelling.`);
        return;
      }
  
      if (isMoviePresent(movies, foundMovie.title)) {
        setWarning(`‘${foundMovie.title}’ already added.`);
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
      setWarning("Failed to search for movie: database might be down");
      console.error("Error searching for movie:", error);
    }
  };
  return (
    <Card className="w-full max-w-md flex flex-col items-center">
      <CardHeader className="flex flex-col items-center text-center">
        <CardTitle>Mediabridge</CardTitle>
        <CardDescription>Add liked movies</CardDescription>
      </CardHeader>
      <CardContent className="w-full">
        <SearchBar
          title={title}
          setTitle={setTitle}
          handleAddMovie={handleAddMovie}
          setSuggestions={setSuggestions}
          suggestions={suggestions}
        />
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