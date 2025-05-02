import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Movie } from "@/types/Movie";
import { searchMovies } from "@/api/movie";

type Props = {
    title: string;
    setTitle: (val: string) => void;
    handleAddMovie: () => void;
    setSuggestions: (movies: Movie[]) => void;
    suggestions: Movie[];
};

const SearchBar = ({ title, setTitle, handleAddMovie, setSuggestions, suggestions }: Props) => {
    const [isFocused, setIsFocused] = useState(false);
    const fetchSuggestions = async (query: string) => {
        if (!query.trim()) return setSuggestions([]);
        try {
            const data = await searchMovies(query);
            const sorted = data.sort((a: Movie, b: Movie) => a.title.localeCompare(b.title));
            setSuggestions(sorted);
        } catch (err) {
            console.error("Failed to fetch suggestions", err);
            setSuggestions([]);
        }
    };

    return (
        <div className="flex w-full flex-col relative space-y-2">
            {/* Group input + button in a horizontal flex container */}
            <div className="flex w-full items-center space-x-4">
                <Input
                    type="text"
                    placeholder="The Room"
                    value={title}
                    onChange={(e) => {
                        const value = e.target.value;
                        setTitle(value);
                        fetchSuggestions(value);
                    }}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => {
                        setTimeout(() => setIsFocused(false), 100);
                    }}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            e.preventDefault();
                            handleAddMovie();
                        }
                    }}
                />
                <Button onClick={handleAddMovie}>Add Movie</Button>
            </div>
            {/* Render dropdown */}
            {isFocused && suggestions.length > 0 && (
                <div className="absolute top-full mt-1 w-full bg-white border border-gray-200 rounded-md shadow-md z-10">
                    {suggestions.map((movie) => (
                        <div
                            key={movie.id}
                            onClick={() => {
                                setTitle(movie.title);
                                setSuggestions([]);
                            }}
                            title={`Released in ${movie.year}`}
                            className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-left"
                        >
                            {movie.title}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default SearchBar;