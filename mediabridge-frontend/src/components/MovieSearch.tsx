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


import axios from "axios"; 

type Props = {
  setMovies: React.Dispatch<React.SetStateAction<Movie[]>>;
};

const MovieSearch = ({ setMovies }: Props) => {
  const [title, setTitle] = useState("");

  const handleAddMovie = async () => {
    if (!title.trim()) return;
  
    try {
      const response = await axios.get("http://127.0.0.1:5000/api/v1/movie/search", {
        params: { q: title },
      });
      const data = response.data;
  
      const foundMovie = data.find(
        (movie: { title: string }) => movie.title.toLowerCase() === title.toLowerCase()
      );
  
      if (!foundMovie) {
        toast({
          title: "Movie not found in database",
          variant: "destructive",
        });
        return;
      }
  
      setMovies((prev) => {
        const alreadyAdded = prev.some(
          (movie) => movie.title.toLowerCase() === foundMovie.title.toLowerCase()
        );
  
        if (alreadyAdded) {
          toast({
            title: "Movie already added",
            variant: "destructive",
          });
          return prev; 
        }
  
        return [
          ...prev,
          {
            id: foundMovie.id.toString(),
            title: foundMovie.title,
            year: foundMovie.year || new Date().getFullYear(),
            image: `https://picsum.photos/seed/${foundMovie.id}/200/300`,
          },
        ];
      });
  
      setTitle("");
    } catch (error) {
      console.error("Error searching for movie:", error);
      toast({
        title: "Failed to Search for movie",
        description: "Database might be down",
        variant: "destructive",
      });
    }
  };

  return (
    <Card className="w-full max-w-md flex flex-col items-center mb-4">
      <CardHeader>
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