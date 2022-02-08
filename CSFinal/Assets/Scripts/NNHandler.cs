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

    void Start()
    {
//        Debug.Log("Game Start");
        dimensions[0] = camera.targetTexture.width;
        dimensions[1] = camera.targetTexture.height;
        //byteArray = new byte[(camera.targetTexture.width * camera.targetTexture.height * 3 * 4) + 8];
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
        //Debug.Log(camera.targetTexture.width + 2000000);
        //Debug.Log(camera.targetTexture.height + 3000000);
        //Debug.Log(a.Length);
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
        //RenderTexture.active = currentRT;
    }

    private void add_to_byteArray(float[] input)
    {
        if (byteArray == null)
        {
            byteArray = new byte[input.Length * 4 + 8];
        }
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
