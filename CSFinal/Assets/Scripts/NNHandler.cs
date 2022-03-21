using System;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using UnityEngine;
using UnityEngine.UI;


public class NNHandler : MonoBehaviour
{
    // Start is called before the first frame update
    public Camera camera;
    private byte[] byteArray = null;
    public CommunicationClient client;
    public int[] dimensions= new int[2];
    public int[] touchinga = new int[1];

    void Start()
    {
//        Debug.Log("Game Start");
        dimensions[0] = camera.targetTexture.width;
        dimensions[1] = camera.targetTexture.height;
        //byteArray = new byte[(camera.targetTexture.width * camera.targetTexture.height * 3 * 4) + 8];
    }

    public Texture2D GetTexture2D()
    {
        var currentRT = RenderTexture.active;
        RenderTexture.active = camera.targetTexture;


        // Render the camera's view.
        camera.Render();

        // Make a new texture and read the active Render Texture into it.
        Texture2D image = new Texture2D(camera.targetTexture.width, camera.targetTexture.height);
        image.ReadPixels(new Rect(0, 0, camera.targetTexture.width, camera.targetTexture.height), 0, 0);
        image.Apply();
        RenderTexture.active = currentRT;
        return image;
    }

    public float[] get_pixel_data(Texture2D image)
    {
        var a = image.GetRawTextureData<byte>();
        float[] pixels = new float[camera.targetTexture.width * camera.targetTexture.height * 3];

        for (int i = 0; i < camera.targetTexture.width; i++)
        {
            for (int j = 0; j < camera.targetTexture.height; j++)
            {
                Color pixel = image.GetPixel(i, j);
                var offset = (i * camera.targetTexture.height + j) * 3;
                pixels[offset + 0] = pixel[0];
                pixels[offset + 1] = pixel[1];
                pixels[offset + 2] = pixel[2];
            }
        }
        return pixels;
    }

    public void CombineData(float[] pixels)
    {
        if (byteArray == null)
        {
            byteArray = new byte[4 + 8 + pixels.Length * 4]; //  sizeof(int) + sizeof(int)*2 + input.Length*sizeof(float)
        }                                                    // touching + dimensions + pixel data
        Buffer.BlockCopy(touchinga, 0, byteArray, 0, 4);
        Buffer.BlockCopy(dimensions, 0, byteArray, 4, 8);
        Buffer.BlockCopy(pixels, 0, byteArray, 4 + 8, pixels.Length * 4);
    }

    public void SendData(bool touching, Action<byte[]> onOutputReceived)
    {   
        if (touching)
        {
            touchinga[0] = 1;
        }
        else
        {
            touchinga[0] = 0;
        }
        Texture2D image = GetTexture2D();
        float[] pixels = get_pixel_data(image);
        CombineData(pixels);
        client.SendData(byteArray, onOutputReceived, error =>
        {
            // TODO: when i am not lazy
        });
    }

    

    public void SendUI()
    {
//        var watch = new System.Diagnostics.Stopwatch();
//        watch.Start();
        var currentRT = RenderTexture.active;
        RenderTexture.active = camera.targetTexture;


        // Render the camera's view.
        camera.Render();

        // Make a new texture and read the active Render Texture into it.
        Texture2D image = new Texture2D(camera.targetTexture.width, camera.targetTexture.height);
        image.ReadPixels(new Rect(0, 0, camera.targetTexture.width, camera.targetTexture.height), 0, 0);
        image.Apply();

        var a = image.GetRawTextureData<byte>();
        float[] arr = new float[camera.targetTexture.width * camera.targetTexture.height * 3];

        for (int i = 0; i < camera.targetTexture.width; i++)
        {
            for (int j = 0; j < camera.targetTexture.height; j++)
            {
                Color pixel = image.GetPixel(i, j);
                var offset = (i * camera.targetTexture.height + j) *3;
                arr[offset + 0] = pixel[0];
                arr[offset + 1] = pixel[1];
                arr[offset + 2] = pixel[2];
                /*Debug.Log(arr[i * j * 3 + 0]);
                Debug.Log(arr[i * j * 3 + 1]);
                Debug.Log(arr[i * j * 3 + 2]);*/
            }
        }
        add_to_byteArray(arr);
        /*client.Predict(arr, output =>
        {
            Debug.Log("Received");
            watch.Stop();
            Debug.Log(watch.ElapsedMilliseconds);
        }, error =>
        {
            // TODO: when i am not lazy
        });*/
        client.SendData(byteArray, output =>
        {
            Debug.Log("Received");
//            watch.Stop();
//            Debug.Log(watch.ElapsedMilliseconds);
        }, error =>
        {
            // TODO: when i am not lazy
        });


        // Replace the original active Render Texture.
        //
    }

    private void add_to_byteArray(float[] input)
    {
        if (byteArray == null)
        {
            byteArray = new byte[4 + 8 + input.Length * 4]; //  sizeof(int) + sizeof(int)*2 + input.Length*sizeof(float)
        }                                                   // touching + dimensions + pixel data
        /*Debug.Log(input.Length + 20000000);
        Debug.Log(byteArray.Length + 1000000);*/
        Buffer.BlockCopy(dimensions, 0, byteArray, 0, 8);
        Buffer.BlockCopy(input, 0, byteArray, 8, input.Length * 4);
/*        for( int i = 0; i < byteArray.Length; i ++)
        {
            Debug.Log(byteArray[i]);
        }*/
    }
}
