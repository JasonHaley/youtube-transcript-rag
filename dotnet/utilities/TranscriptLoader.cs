using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

public class TranscriptEnriched
{
    public string Speaker { get; set; }
    public string Title { get; set; }
    public string VideoId { get; set; }
    public string Description { get; set; }
    public string Start { get; set; }
    public int Seconds { get; set; }
    public string Text { get; set; }
    public float[] Ada_V2 { get; set; }
}

public static class TranscriptLoader
{

    public static List<T> Load<T>(string source)
    {
        try
        {
            var transcript = JsonSerializer.Deserialize<List<T>>(File.ReadAllText(source), 
                new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

            return transcript;
        }
        catch (Exception e)
        {
            Console.WriteLine("Something went wrong: " + e.Message);
            return new List<T>();
        }
    }
}