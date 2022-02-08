using System;
using UnityEngine;

public class CommunicationClient : MonoBehaviour
{
    private MessageHandler messageHandler;

    private void Start() => InitializeServer();

    public void InitializeServer()
    {
        messageHandler = new messageHandler();
        messageHandler.Start();
    }

    public void Predict(float[] input, Action<float[]> onOutputReceived, Action<Exception> fallback)
    {
        messageHandler.SetOnTextReceivedListener(onOutputReceived, fallback);
        messageHandler.SendInput(input);
    }

    public void SendData(byte[] byteArray, Action<float[]> onOutputReceived, Action<Exception> fallback)
    {
        messageHandler.SetOnTextReceivedListener(onOutputReceived, fallback);
        messageHandler.SendInputUpdated(byteArray);
    }

    private void OnDestroy()
    {
        messageHandler.Stop();
    }
}