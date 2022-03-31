using System;
using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using UnityEngine;
using System.Collections;
//new
using System.Diagnostics;
public class MessageHandler : RunAbleThread
{
    private RequestSocket client;

    private Action<byte[]> onOutputReceived;
    private Action<Exception> onFail;

    private string portNum = "6555";
    
    protected override void Run()
    {
        /*var args = System.Environment.GetCommandLineArgs();
        UnityEngine.Debug.Log(args.Length);
        if (args.Length > 1)
        {
            this.portNum = args[1];
        }*/

        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (RequestSocket client = new RequestSocket())
        {
            this.client = client;
            this.portNum = this.tryGetPortNum();
            client.Connect("tcp://localhost:"+this.portNum);

            while (Running)
            {
                byte[] outputBytes = new byte[0];
                bool gotMessage = false;
                while (Running)
                {
                    try
                    {
                        gotMessage = client.TryReceiveFrameBytes(out outputBytes); // this returns true if it's successful
                        if (gotMessage) break;
                    }
                    catch (Exception e)
                    {
                    }
                }

                if (gotMessage)
                {
                    onOutputReceived?.Invoke(outputBytes);
                }
            }
        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
    }

    private string tryGetPortNum()
    {
        var args = System.Environment.GetCommandLineArgs();
        int tmp = 0;
        if (args.Length > 1)
        {
            if (int.TryParse(args[1], out tmp))
            {
                return args[1];
            }
        }
        return this.portNum;
    }

    public void SendInput(float[] input)
    {
        //Stopwatch stopWatch = new Stopwatch();
        //stopWatch.Start();
        try
        {
            //UnityEngine.Debug.Log(input.Length);
            //int alength = input.Length * 4; 
            //var byteArray = new byte[alength* 1];
            var byteArray = new byte[input.Length * 4];
            Buffer.BlockCopy(input, 0, byteArray, 0, byteArray.Length);
            client.SendFrame(byteArray);

        }
        catch (Exception e)
        {
            onFail(e);
        }
        //stopWatch.Stop();
        //UnityEngine.Debug.Log(stopWatch.Elapsed);
    }

    public void SendInputUpdated(byte[] byteArray)
    {
        try
        {
            // UnityEngine.Debug.Log(byteArray.Length);
            client.SendFrame(byteArray);
        }
        catch (Exception e)
        {
            onFail(e);
        }
    }

    public void SetOnTextReceivedListener(Action<byte[]> onOutputReceived, Action<Exception> fallback)
    {
        this.onOutputReceived = onOutputReceived;
        onFail = fallback;
    }

}