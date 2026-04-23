module Main where
greeting :: String
greeting = "hi"
greet :: String -> String
greet name = greeting ++ " " ++ name
main :: IO ()
main = putStrLn (greet "world")
