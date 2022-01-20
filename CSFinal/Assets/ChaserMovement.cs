using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;

public class ChaserMovement : MonoBehaviour
{
    public bool grounded = false;
    Vector3 speed = new Vector3(0, 0, 0);
    public float xDir = 0;
    float moveSpeedRatio = 0.02f;
    float moveSpeedCap = 0.2f;
    float baseJumpSpeed = 0.3f;
    float footPos = 0;
    float gravity = 0.01f;
    int timer = 30;
    int randDir = 1;
    public BoxCollider2D boxCollider2d;
    public Rigidbody2D rigidbody2D;
    void Start()
    {
        Rigidbody2D rigidbody2D = GetComponent<Rigidbody2D>();
        BoxCollider2D boxCollider2d = GetComponent<BoxCollider2D>();
    }

    // Update is called once per frame
    void Update()
    {
        xDir = 0;
        //Input
        if (randDir == 0)
        {
            xDir -= 1;
        }
        if (randDir == 1)
        {
            xDir += 1;
        }
        if (Math.Abs(speed.x) < moveSpeedCap || Math.Sign(speed.x) != Math.Sign(xDir))
        {
            speed.x += moveSpeedRatio * xDir;
        }
        if (grounded && UnityEngine.Random.Range(0.0f, 10.0f) > 9.95f)
        {
            Debug.Log("jump");
            speed.y = baseJumpSpeed;
        }

    }

    void FixedUpdate()
    {
        timer--;
        if (timer <= 0)
        {
            randDir = UnityEngine.Random.Range(0, 2);
            timer = UnityEngine.Random.Range(10, 40);
        }
        Vector3 tmp = rigidbody2D.gameObject.transform.position;
        grounded = IsGrounded();
        if (!grounded)
        {
            speed.y -= gravity;
        }
        if (grounded && speed.y < 0)
        {
            Debug.Log("hit ground");
            speed.y = 0;
        }
        if (IsHittingCeiling())
        {
            speed.y = -0.05f;
        }

        /*if (IsHittingLeftWall() || IsHittingRightWall())
        {
            speed.x = 0;
        }*/
        footPos = tmp.y - .5f;
        rigidbody2D.MovePosition(tmp + speed);
    }

    public bool IsGrounded()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.down, 0.01f);
        return hit.collider != null;
    }
    public bool IsHittingCeiling()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.up, 0.01f);
        return hit.collider != null;
    }

    public bool IsHittingRightWall()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.right, 0.01f);
        return hit.collider != null;
    }

    public bool IsHittingLeftWall()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.left, 0.01f);
        return hit.collider != null;
    }
}
