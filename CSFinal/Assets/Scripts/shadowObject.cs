using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class shadowObject : MonoBehaviour
{
    public GameObject shadow;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        Vector3 tmp = shadow.transform.position;
        tmp.z = 7;
        gameObject.transform.position = tmp;
    }
}
